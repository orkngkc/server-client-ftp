import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os

clients = {}
files = []  # Sunucuda mevcut dosyaların listesi
file_owners = {}  # Dosya sahiplerini takip etmek için


# Server files directory
FILES_DIR = "server_files"
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

def load_existing_files():
    """server_files klasöründeki mevcut dosyaları yükler."""
    global files
    files = os.listdir(FILES_DIR)
    log_message("server_files klasöründeki dosyalar yüklendi.")
    log_message(f"Yüklü dosyalar: {', '.join(files) if files else 'Hiç dosya yok.'}")

def broadcast_file_list():
    """Tüm istemcilere güncellenmiş dosya listesini gönderir."""
    file_list = "\n".join(files) if files else "Sunucuda dosya yok."
    for client in list(clients.keys()):
        try:
            client.send(f"LIST:{file_list}".encode())
        except:
            client.close()
            del clients[client]

def handle_client(client_socket, client_address):
    """İstemciyi yönetir."""
    try:
        username = client_socket.recv(1024).decode()

        # Kullanıcı adı kontrolü
        if username in clients.values():
            client_socket.send("ERROR: Kullanıcı adı zaten kullanılıyor.".encode())
            client_socket.close()
            return

        clients[client_socket] = username
        log_message(f"{username} ({client_address}) bağlandı.")

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
                    log_message(f"{new_file_name} dosyası zaten mevcut. Üzerine yazılıyor.")
                else:
                    files.append(new_file_name)
                    log_message(f"{new_file_name} dosyası kaydedildi ve listeye eklendi.")
                    file_owners[new_file_name] = username  # Track ownership
                broadcast_file_list()
            elif header.startswith("DELETE:"):
                file_name = header[7:]
                if file_name in files and file_owners.get(file_name) == username:
                    os.remove(os.path.join(FILES_DIR, file_name))
                    files.remove(file_name)
                    del file_owners[file_name]
                    log_message(f"{username} dosyayı sildi: {file_name}")
                    broadcast_file_list()
                else:
                    client_socket.send("ERROR: Dosya silme yetkiniz yok ya da bu dosya bulunmuyor.".encode())

            elif header.startswith("LIST"):
                log_message(f"{username} dosya listesini talep etti.")
                file_list = "\n".join(files) if files else "Sunucuda dosya yok."
                client_socket.send(f"LIST:{file_list}".encode())

            elif header.startswith("DOWNLOAD:"):
                requested_file = header[9:]
                requested_path = os.path.join(FILES_DIR, requested_file)

                if requested_file in files and os.path.exists(requested_path):
                    client_socket.send(f"FILE:{requested_file}".encode())
                    with open(requested_path, "rb") as f:
                        client_socket.send(f.read())
                    log_message(f"{username}, {requested_file} dosyasını indirdi.")

                    # Notify the file owner
                    file_owner = file_owners.get(requested_file)
                    if file_owner and file_owner != username:
                        for client, owner in clients.items():
                            if owner == file_owner:
                                client.send(f"NOTIFY: {username} dosyanızı indirdi: {requested_file}".encode())
                else:
                    client_socket.send("ERROR: Dosya bulunamadı.".encode())

            elif header.startswith("NOTIFY:"):
                log_message(header[7:])
                


    except Exception as e:
        log_message(f"Hata: {e}")
    finally:
        if client_socket in clients:
            log_message(f"{clients[client_socket]} bağlantıyı kesti.")
            del clients[client_socket]
        client_socket.close()

def log_message(message):
    """Log mesajlarını GUI'ye ekler."""
    log_area.insert(tk.END, f"{message}\n")
    log_area.yview(tk.END)

def start_server_thread():
    threading.Thread(target=start_server, daemon=True).start()

def start_server():
    """Sunucuyu başlatır."""
    load_existing_files()  # Mevcut dosyaları yükle

    host = "0.0.0.0"
    port = int(port_entry.get())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    log_message(f"Sunucu {host}:{port} üzerinde başlatıldı.")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# GUI
app = tk.Tk()
app.title("Sunucu")

tk.Label(app, text="Port:").pack(pady=5)
port_entry = tk.Entry(app)
port_entry.pack(pady=5)
port_entry.insert(0, "12345")

start_button = tk.Button(app, text="Sunucuyu Başlat", command=start_server_thread)
start_button.pack(pady=5)

log_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state="normal", height=20, width=50)
log_area.pack(pady=5)

app.mainloop()