import socket
import threading

def receive_messages(client_socket):
    """Sunucudan gelen mesajları dinler ve ekranda gösterir."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(f"\nYeni mesaj: {message}")
        except:
            print("Sunucu bağlantısı kesildi.")
            break

def main():
    """İstemciyi başlatır."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "127.0.0.1"
    server_port = 12345

    try:
        client_socket.connect((server_ip, server_port))
        print("Sunucuya bağlanıldı. Mesaj göndermek için yazın, çıkmak için 'exit' yazın.")

        # Sunucudan gelen mesajları dinlemek için bir iş parçacığı başlat
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            message = input()
            if message.lower() == "exit":
                print("Bağlantı sonlandırılıyor...")
                client_socket.close()
                break
            client_socket.send(message.encode())

    except ConnectionRefusedError:
        print("Sunucuya bağlanılamadı. Lütfen sunucunun çalıştığından emin olun.")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
