import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog
import os

clients = {}
files = []  # List of files on the server
file_owners = {}  # Tracks file ownership

# Default directory for storing files
FILES_DIR = "server_files"
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

def load_existing_files():
    """Loads existing files from the selected storage directory and assigns ownership."""
    global files, file_owners
    files = os.listdir(FILES_DIR)
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
    for client in list(clients.keys()):
        try:
            client.send(f"LIST:{file_list}".encode())
        except:
            client.close()
            del clients[client]

def handle_client(client_socket, client_address):
    """Handles the client."""
    try:
        username = client_socket.recv(1024).decode()

        if username in clients.values():
            client_socket.send("ERROR: Username already in use.".encode())
            client_socket.close()  # Ensure the socket is closed
            return 

        clients[client_socket] = username
        log_message(f"{username} ({client_address}) connected.")

        while True:
            header = client_socket.recv(1024).decode()

            if header.startswith("FILE:"):
                file_name = header[5:]
                new_file_name = f"{username}_{file_name}"
                file_path = os.path.join(FILES_DIR, new_file_name)

                file_data = client_socket.recv(1024 * 64)
                with open(file_path, "wb") as f:
                    f.write(file_data)

                if new_file_name in files:
                    log_message(f"The file {new_file_name} already exists. Overwriting.")
                else:
                    files.append(new_file_name)
                    log_message(f"The file {new_file_name} was saved and added to the list.")
                    file_owners[new_file_name] = username  # Track ownership
                broadcast_file_list()
            elif header.startswith("DELETE:"):
                file_name = header[7:]
                if file_name in files and file_owners.get(file_name) == username:
                    os.remove(os.path.join(FILES_DIR, file_name))
                    files.remove(file_name)
                    del file_owners[file_name]
                    log_message(f"{username} deleted the file: {file_name}")
                    broadcast_file_list()
                else:
                    client_socket.send("ERROR: You do not have permission to delete this file or the file does not exist.".encode())

            elif header.startswith("LIST"):
                log_message(f"{username} requested the file list.")
                file_list = "\n".join(files) if files else "No files on the server."
                client_socket.send(f"LIST:{file_list}".encode())

            elif header.startswith("DOWNLOAD:"):
                requested_file = header[9:]
                requested_path = os.path.join(FILES_DIR, requested_file)

                if requested_file in files and os.path.exists(requested_path):
                    client_socket.send(f"FILE:{requested_file}".encode())
                    with open(requested_path, "rb") as f:
                        while chunk := f.read(1024 * 64):  # Send the file in chunks
                            client_socket.send(chunk)
                    client_socket.send(b"EOF")  # Signal the end of the file transfer
                    log_message(f"{username} downloaded the file: {requested_file}")
                else:
                    client_socket.send("ERROR: File not found.".encode())
    except Exception as e:
        log_message(f"Error: {e}")
    finally:
        if client_socket in clients:
            log_message(f"{clients[client_socket]} disconnected.")
            del clients[client_socket]
        client_socket.close()

def log_message(message):
    """Adds log messages to the GUI."""
    log_area.insert(tk.END, f"{message}\n")
    log_area.yview(tk.END)

def change_directory():
    """Changes the directory for storing files."""
    global FILES_DIR
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        FILES_DIR = selected_dir
        load_existing_files()
        log_message(f"The storage directory was changed to: {FILES_DIR}")

def start_server_thread():
    threading.Thread(target=start_server, daemon=True).start()

def start_server():
    """Starts the server."""
    load_existing_files()

    host = "0.0.0.0"
    port = int(port_entry.get())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    log_message(f"Server started on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# GUI
app = tk.Tk()
app.title("Server")

tk.Label(app, text="Port:").pack(pady=5)
port_entry = tk.Entry(app)
port_entry.pack(pady=5)
port_entry.insert(0, "12345")

tk.Button(app, text="Select Storage Directory", command=change_directory).pack(pady=5)

start_button = tk.Button(app, text="Start Server", command=start_server_thread)
start_button.pack(pady=5)

log_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state="normal", height=20, width=50)
log_area.pack(pady=5)

app.mainloop()
# End of server_gui.py