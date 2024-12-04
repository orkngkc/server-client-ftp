import socket
import threading

clients = []  # Bağlı istemcilerin listesi

def broadcast(message, sender_socket):
    """Bir istemciden gelen mesajı diğer istemcilere iletir."""
    for client in clients:
        if client != sender_socket:  # Mesajı gönderen istemciye geri gönderme
            try:
                client.send(message)
            except:
                # Hata durumunda istemciyi listeden çıkar
                clients.remove(client)

def handle_client(client_socket, client_address):
    """İstemciyi yönetir ve mesajlarını diğer istemcilere iletir."""
    print(f"Yeni bağlantı: {client_address}")
    clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"Gelen mesaj {client_address}: {message.decode()}")
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            break

    print(f"Bağlantı kesildi: {client_address}")
    client_socket.close()

def main():
    """Sunucuyu başlatır."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Sunucu {host}:{port} üzerinde dinleniyor...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()

