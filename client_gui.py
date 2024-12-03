import socket
import threading
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, END
def receive_messages(client_socket, text_area):
    """Listen for messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                text_area.insert(END, f"{message}\n")
                text_area.see(END)  # Auto-scroll to the latest message
        except Exception as e:
            text_area.insert(END, f"Disconnected from server: {e}\n")
            text_area.see(END)
            break


def send_message(client_socket, message_entry, text_area):
    """Send a message to the server."""
    message = message_entry.get().strip()
    if message:
        try:
            client_socket.send(message.encode())
            message_entry.delete(0, END)
        except:
            text_area.insert(END, "Error sending message. Disconnected from server.\n")
            text_area.see(END)

def connect_to_server(ip, port, name, text_area, message_entry):
    """Connect to the server and start message handling."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip, int(port)))
        text_area.insert(END, f"Connected to server at {ip}:{port}\n")
        client_socket.send(name.encode())

        threading.Thread(target=receive_messages, args=(client_socket, text_area), daemon=True).start()

        send_button.config(command=lambda: send_message(client_socket, message_entry, text_area))
        send_button.pack()
    except Exception as e:
        text_area.insert(END, f"Error connecting to server: {e}\n")
        text_area.see(END)

# GUI setup
root = Tk()
root.title("Client GUI")

Label(root, text="Server IP:").pack()
ip_entry = Entry(root)
ip_entry.pack()

Label(root, text="Port:").pack()
port_entry = Entry(root)
port_entry.pack()

Label(root, text="Name:").pack()
name_entry = Entry(root)
name_entry.pack()

connect_button = Button(root, text="Connect", command=lambda: connect_to_server(
    ip_entry.get(), port_entry.get(), name_entry.get(), text_area, message_entry))
connect_button.pack()

text_area = Text(root, height=20, width=50)
text_area.pack()

scrollbar = Scrollbar(root, command=text_area.yview)
text_area.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

message_entry = Entry(root, width=40)
message_entry.pack()

send_button = Button(root, text="Send")  # Button configured after connection

root.mainloop()
