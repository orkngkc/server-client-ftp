import socket  
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import os
def receive_messages(): 
    """Listens for messages from the server and displays them on the screen."""
    while True:     
        try:    
            message = client_socket.recv(1024).decode() # Receive message from server

            if message.startswith("FILE:"):  # Check if the message is a file transfer
                file_name = message[5:]  # Extract the file name
                log_message(f"Preparing to download file: {file_name}")
                
                # Open a directory selection dialog
                directory = filedialog.askdirectory(title="Select Directory to Save File")
                if not directory:  # If no directory is selected
                    log_message("Download cancelled: No directory selected.")
                    continue  # Skip the current iteration

                # Define the full path where the file will be saved
                file_path = os.path.join(directory, file_name)
                log_message(f"Saving to: {file_path}")

                # Initialize a byte string to receive the file data
                file_data = b""
                while True:
                    chunk = client_socket.recv(1024 * 64)  # Receive data in 64 KB chunks
                    if b"EOF" in chunk:  # Check for EOF signal
                        file_data += chunk.replace(b"EOF", b"")  # Remove EOF marker
                        break
                    file_data += chunk

                # Save the received data to the selected path
                try:
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                    log_message(f"File successfully downloaded and saved to: {file_path}")
                except Exception as e:
                    log_message(f"Error saving file: {e}")


            elif message.startswith("LIST:"):  # Check if the message is a file list
                file_list = message[5:]   # Extract the file list from the message
                log_message(f"File List:\n{file_list}")  # Log the file list

            elif message.startswith("ERROR:"):      # Check if the message is an error message
                if message == "ERROR: Username already in use.":
                    client_socket.close()
                log_message(message)

            else:   # If the message is a regular text message
                log_message(f"From server: {message}")  # Log the message
        except Exception as e:  # Handle exceptions
            log_message(f"Error: {e}")  # Log the error
            break
        
def delete_file():     # Function to delete a file 
    file_name = delete_file_name_entry.get() # Get the file name from the entry widget
    if file_name:  # Check if the file name is not empty
        try:
            client_socket.send(f"DELETE:{file_name}".encode()) # Send the delete request to the server
            log_message(f"Delete request sent: {file_name}") # Log the delete request
        except Exception as e:  # Handle exceptions
            log_message(f"Error: {e}")
    else:
        messagebox.showerror("Error", "Please enter a file name to delete.")

def send_file():   # Function to send a file
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")]) # Open a file dialog to select a file
    if not file_path:   # Check if a file was selected
        return  # Exit the function if no file was selected

    try:    # Try to send the file
        file_name = file_path.split("/")[-1]    # Extract the file name from the file path
        client_socket.send(f"FILE:{file_name}".encode())    # Send the file name to the server

        with open(file_path, "rb") as f:    # Open the file in read-binary mode
            client_socket.send(f.read())    # Send the file data to the server
        log_message(f"File sent: {file_name}")  # Log the successful file transfer
    except Exception as e:  # Handle exceptions
        log_message(f"Error: {e}")  # Log the error

def request_file_list():    # Function to request the file list from the server
    """Requests the file list from the server."""
    try:
        client_socket.send("LIST".encode()) # Send the list request to the server
    except Exception as e:  # Handle exceptions
        log_message(f"Error: {e}")

def download_file():    # Function to download a file
    file_name = file_name_entry.get()   # Get the file name from the entry widget
    if file_name:   # Check if the file name is not empty
        client_socket.send(f"DOWNLOAD:{file_name}".encode())    # Send the download request to the server
    else:       # If the file name is empty
        messagebox.showerror("Error", "Please enter a file name to download.")

def connect_to_server():    # Function to connect to the server
    global client_socket    # Declare the client_socket as a global variable
    try:    # Try to connect to the server
        server_ip = server_ip_entry.get()   # Get the server IP address from the entry widget
        server_port = int(server_port_entry.get())  # Get the server port number from the entry widget
        username = username_entry.get() # Get the username from the entry widget

        if not username:    # Check if the username is empty
            messagebox.showerror("Error", "Username cannot be empty!")  # Show an error message
            return  # Exit the function

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Create a new socket
        client_socket.connect((server_ip, server_port)) # Connect to the server
        client_socket.send(username.encode())   # Send the username to the server

        threading.Thread(target=receive_messages, daemon=True).start()  # Start a new thread to receive messages
        log_message("Connected to the server.")   # Log the successful connection
    except Exception as e:
        messagebox.showerror("Error", f"Unable to connect: {e}")
        client_socket.close()

def log_message(message):   # Function to log messages in the chat area
    chat_area.insert(tk.END, f"{message}\n")    # Insert the message at the end of the chat area
    chat_area.yview(tk.END)

def disconnect_from_server():
    """Disconnects the client from the server and closes the application."""
    global client_socket
    try:
        client_socket.send("DISCONNECT".encode())  # Inform the server of disconnection
        client_socket.close()  # Close the client socket
        log_message("Disconnected from the server.")
    except Exception as e:
        log_message(f"Error during disconnection: {e}")
    finally:
        app.destroy()  # Close the client application window
# GUI
app = tk.Tk()   # Create the main application window
app.title("File Client")    # Set the title of the window

tk.Label(app, text="Server IP:").pack()   # Create a label widget
server_ip_entry = tk.Entry(app) # Create an entry widget
server_ip_entry.pack()  # Place the entry widget in the window
server_ip_entry.insert(0, "127.0.0.1")  # Set the default server IP address

tk.Label(app, text="Port:").pack()  # Create a label widget
server_port_entry = tk.Entry(app)   # Create an entry widget
server_port_entry.pack()        # Place the entry widget in the window
server_port_entry.insert(0, "12345")    # Set the default server port number

tk.Label(app, text="Username:").pack()  # Create a label widget  
username_entry = tk.Entry(app)      # Create an entry widget
username_entry.pack()        # Place the entry widget in the window

tk.Button(app, text="Connect", command=connect_to_server).pack()    # Create a button widget For connecting to the server
tk.Button(app, text="Send File", command=send_file).pack()      # Create a button widget for sending files
tk.Button(app, text="Request File List", command=request_file_list).pack()  # Create a button widget   for requesting the file list

tk.Label(app, text="File to Delete:").pack()    # Create a label widget for deleting files
delete_file_name_entry = tk.Entry(app)  # Create an entry widget for deleting files
delete_file_name_entry.pack()   # Place the entry widget in the window
tk.Button(app, text="Delete File", command=delete_file).pack()  # Create a button widget for deleting files

tk.Label(app, text="File to Download:").pack()  # Create a label widget for downloading files
file_name_entry = tk.Entry(app) # Create an entry widget for downloading files
file_name_entry.pack()  # Place the entry widget in the window

tk.Button(app, text="Download File", command=download_file).pack()  # Create a button widget for downloading files
# Adding a Disconnect button in the GUI
tk.Button(app, text="Disconnect", command=disconnect_from_server).pack()

chat_area = tk.Text(app, wrap=tk.WORD, height=15, width=50) # Create a text widget for displaying chat messages
chat_area.pack()    # Place the text widget in the window

app.mainloop()  # Start the main event loop
