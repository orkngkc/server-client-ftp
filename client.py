import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

def receive_messages():
    """Sunucudan gelen mesajları dinler ve ekranda gösterir."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith("LIST:"):
                file_list = message[5:]
                log_message(f"Dosya Listesi:\n{file_list}")
            elif message.startswith("FILE:"):
                file_name = message[5:]
                file_data = client_socket.recv(1024 * 64)

                with open(file_name, "wb") as f:
                    f.write(file_data)
                log_message(f"Dosya indirildi: {file_name}")
            elif message.startswith("ERROR:"):
                log_message(message)
            else:
                log_message(f"Sunucudan: {message}")
        except Exception as e:
            log_message(f"Hata: {e}")
            break


def send_file():
    file_path = filedialog.askopenfilename(filetypes=[("Tüm Dosyalar", "*.*")])
    if not file_path:
        return

    try:
        file_name = file_path.split("/")[-1]
        client_socket.send(f"FILE:{file_name}".encode())

        with open(file_path, "rb") as f:
            client_socket.send(f.read())
        log_message(f"Dosya gönderildi: {file_name}")
    except Exception as e:
        log_message(f"Hata: {e}")

def request_file_list():
    """Dosya listesini sunucudan talep eder."""
    try:
        client_socket.send("LIST".encode())
    except Exception as e:
        log_message(f"Hata: {e}")

def download_file():
    file_name = file_name_entry.get()
    if file_name:
        client_socket.send(f"DOWNLOAD:{file_name}".encode())
    else:
        messagebox.showerror("Hata", "İndirmek için bir dosya adı girin.")

def connect_to_server():
    global client_socket
    try:
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())
        username = username_entry.get()

        if not username:
            messagebox.showerror("Hata", "Kullanıcı adı boş olamaz!")
            return

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_socket.send(username.encode())

        threading.Thread(target=receive_messages, daemon=True).start()
        log_message("Sunucuya bağlanıldı.")
    except Exception as e:
        messagebox.showerror("Hata", f"Bağlanılamadı: {e}")

def log_message(message):
    chat_area.insert(tk.END, f"{message}\n")
    chat_area.yview(tk.END)

# GUI
app = tk.Tk()
app.title("Dosya İstemcisi")

tk.Label(app, text="Sunucu IP:").pack()
server_ip_entry = tk.Entry(app)
server_ip_entry.pack()
server_ip_entry.insert(0, "127.0.0.1")

tk.Label(app, text="Port:").pack()
server_port_entry = tk.Entry(app)
server_port_entry.pack()
server_port_entry.insert(0, "12345")

tk.Label(app, text="Kullanıcı Adı:").pack()
username_entry = tk.Entry(app)
username_entry.pack()

tk.Button(app, text="Bağlan", command=connect_to_server).pack()
tk.Button(app, text="Dosya Gönder", command=send_file).pack()
tk.Button(app, text="Dosya Listesi", command=request_file_list).pack()

tk.Label(app, text="İndirmek İstediğiniz Dosya:").pack()
file_name_entry = tk.Entry(app)
file_name_entry.pack()

tk.Button(app, text="Dosya İndir", command=download_file).pack()

chat_area = tk.Text(app, wrap=tk.WORD, height=15, width=50)
chat_area.pack()

app.mainloop()
