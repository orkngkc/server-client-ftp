import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

def receive_messages():
    """Listens for messages from the server and displays them on the screen."""
    while True:
        try:
            message = client_socket.recv(1024).decode()

            if message.startswith("FILE:"):
                file_name = message[5:]
                log_message(f"Downloading file: {file_name}")
                
                with open(file_name, "wb") as f:
                    while True:
                        chunk = client_socket.recv(1024 * 64)
                        if chunk == b"EOF":  # Check for end-of-file signal
                            break
                        f.write(chunk)
                log_message(f"File downloaded: {file_name}")

            elif message.startswith("LIST:"):
                file_list = message[5:]
                log_message(f"File List:\n{file_list}")

            elif message.startswith("ERROR:"):
                log_message(message)

            else:
                log_message(f"From server: {message}")
        except Exception as e:
            log_message(f"Error: {e}")
            break
        
def delete_file():
    file_name = delete_file_name_entry.get()
    if file_name:
        try:
            client_socket.send(f"DELETE:{file_name}".encode())
            log_message(f"Delete request sent: {file_name}")
        except Exception as e:
            log_message(f"Error: {e}")
    else:
        messagebox.showerror("Error", "Please enter a file name to delete.")

def send_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if not file_path:
        return

    try:
        file_name = file_path.split("/")[-1]
        client_socket.send(f"FILE:{file_name}".encode())

        with open(file_path, "rb") as f:
            client_socket.send(f.read())
        log_message(f"File sent: {file_name}")
    except Exception as e:
        log_message(f"Error: {e}")

def request_file_list():
    """Requests the file list from the server."""
    try:
        client_socket.send("LIST".encode())
    except Exception as e:
        log_message(f"Error: {e}")

def download_file():
    file_name = file_name_entry.get()
    if file_name:
        client_socket.send(f"DOWNLOAD:{file_name}".encode())
    else:
        messagebox.showerror("Error", "Please enter a file name to download.")

def connect_to_server():
    global client_socket
    try:
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())
        username = username_entry.get()

        if not username:
            messagebox.showerror("Error", "Username cannot be empty!")
            return

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_socket.send(username.encode())

        threading.Thread(target=receive_messages, daemon=True).start()
        log_message("Connected to the server.")
    except Exception as e:
        messagebox.showerror("Error", f"Unable to connect: {e}")

def log_message(message):
    chat_area.insert(tk.END, f"{message}\n")
    chat_area.yview(tk.END)

# GUI
app = tk.Tk()
app.title("File Client")

tk.Label(app, text="Server IP:").pack()
server_ip_entry = tk.Entry(app)
server_ip_entry.pack()
server_ip_entry.insert(0, "127.0.0.1")

tk.Label(app, text="Port:").pack()
server_port_entry = tk.Entry(app)
server_port_entry.pack()
server_port_entry.insert(0, "12345")

tk.Label(app, text="Username:").pack()
username_entry = tk.Entry(app)
username_entry.pack()

tk.Button(app, text="Connect", command=connect_to_server).pack()
tk.Button(app, text="Send File", command=send_file).pack()
tk.Button(app, text="Request File List", command=request_file_list).pack()

tk.Label(app, text="File to Delete:").pack()
delete_file_name_entry = tk.Entry(app)
delete_file_name_entry.pack()
tk.Button(app, text="Delete File", command=delete_file).pack()

tk.Label(app, text="File to Download:").pack()
file_name_entry = tk.Entry(app)
file_name_entry.pack()

tk.Button(app, text="Download File", command=download_file).pack()

chat_area = tk.Text(app, wrap=tk.WORD, height=15, width=50)
chat_area.pack()

app.mainloop()
