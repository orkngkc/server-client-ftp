import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import json

def receive_messages():
    """Sunucudan gelen mesajları dinler ve ekranda gösterir."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            data = json.loads(message)
            chat_area.insert(tk.END, f"{data['username']}: {data['message']}\n")
            chat_area.yview(tk.END)
        except:
            messagebox.showwarning("Bağlantı Koptu", "Sunucu bağlantısı kesildi.")
            break

def send_message():
    """Mesajı sunucuya gönder ve kendi ekranda göster."""
    message = message_entry.get()
    if message.lower() == "exit":
        client_socket.close()
        app.quit()
    else:
        data = json.dumps({"username": username, "message": message})
        client_socket.send(data.encode())
        message_entry.delete(0, tk.END)

def connect_to_server():
    """Sunucuya bağlan ve mesajlaşmayı başlat."""
    global client_socket, username
    try:
        server_ip = server_ip_entry.get()
        server_port = int(server_port_entry.get())
        username = username_entry.get()

        if not username:
            messagebox.showerror("Hata", "Kullanıcı adı boş olamaz!")
            return

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_socket.send(username.encode())  # Kullanıcı adı sunucuya gönderilir

        connect_button.config(state=tk.DISABLED)
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Bağlantı Hatası", f"Sunucuya bağlanılamadı: {e}")

# GUI
app = tk.Tk()
app.title("İstemci")

tk.Label(app, text="Sunucu IP:").grid(row=0, column=0, pady=5, padx=5)
server_ip_entry = tk.Entry(app)
server_ip_entry.grid(row=0, column=1, pady=5, padx=5)
server_ip_entry.insert(0, "127.0.0.1")

tk.Label(app, text="Port:").grid(row=1, column=0, pady=5, padx=5)
server_port_entry = tk.Entry(app)
server_port_entry.grid(row=1, column=1, pady=5, padx=5)
server_port_entry.insert(0, "12345")

tk.Label(app, text="Kullanıcı Adı:").grid(row=2, column=0, pady=5, padx=5)
username_entry = tk.Entry(app)
username_entry.grid(row=2, column=1, pady=5, padx=5)

connect_button = tk.Button(app, text="Bağlan", command=connect_to_server)
connect_button.grid(row=3, column=0, columnspan=2, pady=5)

chat_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state="normal", height=15, width=50)
chat_area.grid(row=4, column=0, columnspan=2, pady=5)

tk.Label(app, text="Mesaj:").grid(row=5, column=0, pady=5, padx=5)
message_entry = tk.Entry(app, width=40)
message_entry.grid(row=5, column=1, pady=5, padx=5)

send_button = tk.Button(app, text="Gönder", command=send_message)
send_button.grid(row=6, column=0, columnspan=2, pady=5)

app.mainloop()
