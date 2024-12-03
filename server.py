import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import json

clients = {}  # Bağlı istemcilerin listesi

def broadcast(message):
    """Bir istemciden gelen mesajı tüm istemcilere iletir."""
    for client in clients.keys():
        try:
            client.send(message.encode())
        except:
            client.close()
            del clients[client]

def handle_client(client_socket, client_address):
    """İstemciyi yönetir ve mesajlarını diğer istemcilere iletir."""
    try:
        # Kullanıcı adını al
        username = client_socket.recv(1024).decode()
        clients[client_socket] = username
        log(f"{username} ({client_address}) bağlandı.")

        while True:
            # Mesajı al
            message = client_socket.recv(1024).decode()
            if not message:
                break

            # Mesajı JSON formatında çöz
            try:
                data = json.loads(message)
                log(f"{data['username']}: {data['message']}")

                # Mesajı tüm istemcilere geri ilet
                broadcast(message)
            except json.JSONDecodeError:
                log("Geçersiz JSON formatı alındı.")
    except:
        pass
    finally:
        log(f"{clients[client_socket]} bağlantıyı kesti.")
        del clients[client_socket]
        client_socket.close()

def log(message):
    """Log mesajlarını GUI'ye ekler."""
    log_area.insert(tk.END, f"{message}\n")
    log_area.yview(tk.END)

def start_server():
    """Sunucuyu başlatır."""
    host = "0.0.0.0"
    port = int(port_entry.get())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    log(f"Sunucu {host}:{port} üzerinde başlatıldı.")

    def accept_clients():
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

    threading.Thread(target=accept_clients, daemon=True).start()

# GUI
app = tk.Tk()
app.title("Sunucu")

tk.Label(app, text="Port:").pack(pady=5)
port_entry = tk.Entry(app)
port_entry.pack(pady=5)
port_entry.insert(0, "12345")

start_button = tk.Button(app, text="Sunucuyu Başlat", command=start_server)
start_button.pack(pady=5)

log_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state="normal", height=20, width=50)
log_area.pack(pady=5)

app.mainloop()
