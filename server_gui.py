import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
import os

clients = {}   # List of connected clients
files = []  # List of files on the server
file_owners = {}  # Tracks file ownership

# Default directory for storing files
FILES_DIR = "server_files"
if not os.path.exists(FILES_DIR): # Create the directory if it doesn't exist
    os.makedirs(FILES_DIR)  # Create the directory if it doesn't exist

def load_existing_files():      # Load existing files from the selected storage directory and assigns ownership
    """Loads existing files from the selected storage directory and assigns ownership."""
    global files, file_owners        # Use the global variables
    files = os.listdir(FILES_DIR)           # Get the list of files in the directory
    file_owners.clear()  # Clear existing ownership data

    for file_name in files:
        # Extract ownership from file name if the naming convention includes ownership
        if "_" in file_name:
            owner, actual_file_name = file_name.split("_", 1)  # Split into owner and file name
            file_owners[file_name] = owner  # Assign ownership        
        else:
            log_message(f"Warning: No ownership information found for file: {file_name}")
    
    log_message("Files loaded from the storage directory.")
    log_message(f"Loaded files: {', '.join(files) if files else 'No files found.'}")


def broadcast_file_list():
    """Sends the updated file list to all clients."""   
    file_list = "\n".join(files) if files else "No files on the server."
    for client in list(clients.keys()):         # Use list() to create a copy of the keys
        try:
            client.send(f"LIST:{file_list}".encode())   # Send the updated file list
        except:
            client.close()       # Close the socket
            del clients[client]      # Remove the client from the list

def handle_client(client_socket, client_address):     # Handles the client
    """Handles the client."""
    try:
        username = client_socket.recv(1024).decode()    # Receive the username from the client

        if username in clients.values():       # Check if the username is already in use
            client_socket.send("ERROR: Username already in use.".encode())
            client_socket.close()  # Ensure the socket is closed
            return    # Exit the function   

        clients[client_socket] = username       # Add the client to the list of connected clients
        log_message(f"{username} ({client_address}) connected.")       # Log the connection

        while True:
            header = client_socket.recv(1024).decode()    # Receive the header from the client

            if header.startswith("FILE:"):     # Check if the header is for a file transfer
                file_name = header[5:]     # Extract the file name
                new_file_name = f"{username}_{file_name}"     # Add the username to the file name
                file_path = os.path.join(FILES_DIR, new_file_name)    # Create the file path

                file_data = client_socket.recv(1024 * 64)  # Receive the file data
                with open(file_path, "wb") as f:   # Write the file data to the file
                    f.write(file_data)    # Write the file data to the file

                if new_file_name in files:   # Check if the file already exists
                    log_message(f"The file {new_file_name} already exists. Overwriting.")  # Log the overwrite
                else:
                    files.append(new_file_name)  # Add the file to the list of files
                    log_message(f"The file {new_file_name} was saved and added to the list.")
                    file_owners[new_file_name] = username  # Track ownership
                broadcast_file_list()     # Broadcast the updated file list
            elif header.startswith("DELETE:"):    # Check if the header is for a file deletion
                file_name = header[7:]  # Extract the file name
                if file_name in files and file_owners.get(file_name) == username: # Check if the file exists and the user is the owner
                    os.remove(os.path.join(FILES_DIR, file_name)) # Remove the file from the storage directory
                    files.remove(file_name) # Remove the file from the list of files
                    del file_owners[file_name] # Remove the ownership information
                    log_message(f"{username} deleted the file: {file_name}") # Log the deletion
                    broadcast_file_list()
                else:
                    client_socket.send("ERROR: You do not have permission to delete this file or the file does not exist.".encode())

            elif header.startswith("LIST"): # Check if the header is for a file list request
                log_message(f"{username} requested the file list.") # Log the request
                file_list = "\n".join(files) if files else "No files on the server." 
                client_socket.send(f"LIST:{file_list}".encode()) # Send the file list to the client

            elif header.startswith("DOWNLOAD:"): # Check if the header is for a file download request
                requested_file = header[9:] # Extract the requested file name
                requested_path = os.path.join(FILES_DIR, requested_file) # Create the file path

                if requested_file in files and os.path.exists(requested_path): # Check if the file exists
                    client_socket.send(f"FILE:{requested_file}".encode())
                    with open(requested_path, "rb") as f: 
                        while chunk := f.read(1024 * 64):  # Send the file in chunks
                            client_socket.send(chunk)   
                    client_socket.send(b"EOF")  # Signal the end of the file transfer
                    log_message(f"{username} downloaded the file: {requested_file}") # Log the download
                    file_owner = file_owners.get(requested_file) # Get the owner of the file
                    if file_owner and file_owner != username:  # Ensure the owner is notified only if it's not the downloader
                        for client, owner in clients.items():   
                            if owner == file_owner: # Find the client socket for the owner
                                try:    # Notify the owner of the download
                                    client.send(f"NOTIFY: {username} downloaded your file: {requested_file}".encode())
                                except Exception as e: # Handle any errors
                                    log_message(f"Error notifying {file_owner}: {e}")
                else:
                    client_socket.send("ERROR: File not found.".encode()) # Send an error message if the file is not found
    except Exception as e:  
        log_message(f"Error: {e}")  # Log any errors
    finally:
        if client_socket in clients:    # Check if the client socket is in the list of clients
            log_message(f"{clients[client_socket]} disconnected.") # Log the disconnection
            del clients[client_socket] # Remove the client from the list
        client_socket.close() # Close the client socket

def log_message(message):  # Adds log messages to the GUI
    """Adds log messages to the GUI."""        
    log_area.insert(tk.END, f"{message}\n") # Insert the message at the end of the log area
    log_area.yview(tk.END)  # Scroll to the end of the log area

def change_directory():
    """Changes the directory for storing files."""
    global FILES_DIR # Use the global variable
    selected_dir = filedialog.askdirectory() # Open a dialog to select a directory
    if selected_dir: # Check if a directory was selected
        FILES_DIR = selected_dir    # Update the storage directory
        load_existing_files()  # Reload the files from the new directory
        log_message(f"The storage directory was changed to: {FILES_DIR}" )

def start_server_thread(): # Starts the server in a separate thread
    threading.Thread(target=start_server, daemon=True).start()  # Start the server in a separate thread

def start_server(): # Starts the server
    """Starts the server."""
    load_existing_files()

    host = "0.0.0.0"    # Listen on all network interfaces
    port = int(port_entry.get()) # Get the port number from the entry field

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Create a TCP socket
    server_socket.bind((host, port)) # Bind the socket to the host and port
    server_socket.listen(5) # Listen for incoming connections
    log_message(f"Server started on {host}:{port}") # Log the server start

    while True: # Continuously accept incoming connections
        client_socket, client_address = server_socket.accept()  # Accept a new connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address)) # Create a new thread for the client
        client_thread.start() # Start the client thread

# GUI
app = tk.Tk()  # Create the main application window
app.title("Server")

tk.Label(app, text="Port:").pack(pady=5) # Add a label for the port entry field
port_entry = tk.Entry(app)
port_entry.pack(pady=5)     # Add an entry field for the port
port_entry.insert(0, "12345")   # Set the default port number

tk.Button(app, text="Select Storage Directory", command=change_directory).pack(pady=5) # Add a button to change the storage directory

start_button = tk.Button(app, text="Start Server", command=start_server_thread) # Add a button to start the server
start_button.pack(pady=5) # Pack the start button

log_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state="normal", height=20, width=50) # Add a scrolled text area for logging
log_area.pack(pady=5) # Pack the log area

app.mainloop()
# End of server_gui.py