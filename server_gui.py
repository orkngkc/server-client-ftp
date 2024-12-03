import socket
import threading
from tkinter import Tk, Label, Entry, Button, Listbox, END

# Dictionary to store connected clients (name -> socket)
connected_clients = {}

def broadcast(message, sender_name, log_box):
    """Send a message to all clients except the sender."""
    disconnected_clients = []
    log_box.insert(END, f"Broadcasting: {sender_name}: {message}\n")  # Log the broadcast

    for name, client_socket in connected_clients.items():
        try:
            if name != sender_name:
                client_socket.send(f"{sender_name}: {message}".encode())
        except Exception as e:
            log_box.insert(END, f"Error sending to {name}: {e}\n")
            disconnected_clients.append(name)

    # Remove disconnected clients
    for name in disconnected_clients:
        del connected_clients[name]
        log_box.insert(END, f"{name} removed due to disconnection.\n")

def handle_client(client_socket, client_address, log_box):
    """Handle communication with a single client."""
    try:
        # Receive and validate the client's name
        client_name = client_socket.recv(1024).decode().strip()
        if not client_name or client_name in connected_clients:
            client_socket.send("ERROR: Name already in use or invalid. Disconnecting.".encode())
            log_box.insert(END, f"Invalid or duplicate name attempt from {client_address}\n")
            client_socket.close()
            return

        # Add the client to the connected list
        connected_clients[client_name] = client_socket
        log_box.insert(END, f"{client_name} connected from {client_address}\n")
        broadcast(f"{client_name} has joined the chat.", "Server", log_box)

        # Handle incoming messages
        while True:
            message = client_socket.recv(1024).decode().strip()
            if not message or message.lower() == "exit":
                break
            log_box.insert(END, f"Message from {client_name}: {message}\n")
            broadcast(message, client_name, log_box)

    except Exception as e:
        log_box.insert(END, f"Error with {client_address}: {e}\n")

    finally:
        if client_name in connected_clients:
            del connected_clients[client_name]
            log_box.insert(END, f"{client_name} disconnected.\n")
            broadcast(f"{client_name} has left the chat.", "Server", log_box)
        client_socket.close()

def start_server(port, log_box):
    """Start the server and listen for client connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", int(port)))
    server_socket.listen(5)
    log_box.insert(END, f"Server is listening on port {port}\n")

    def accept_clients():
        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, client_address, log_box), daemon=True).start()

    threading.Thread(target=accept_clients, daemon=True).start()

# GUI setup
root = Tk()
root.title("Server GUI")

Label(root, text="Port:").pack()
port_entry = Entry(root)
port_entry.pack()

log_box = Listbox(root, width=50, height=20)
log_box.pack()

start_button = Button(root, text="Start Server", command=lambda: start_server(port_entry.get(), log_box))
start_button.pack()

root.mainloop()
