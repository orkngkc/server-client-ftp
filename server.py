import socket
import threading

def handle_client(client_socket, client_address):
    """Process data from client"""
    print(f"New Connection: {client_address}")
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:  # if client closes connection
                break
            print(f"Incoming Data: {client_address}: {data}")
            client_socket.send("Hello From Server!".encode())
        except ConnectionResetError:
            print(f"Connection lost: {client_address}")
            break
    client_socket.close()

def main():
    """init server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "0.0.0.0"  # accept all incoming ips
    port = 12345

    server_socket.bind((host, port))
    server_socket.listen(5)  # max5 clients
    print(f"Server listens on {host}:{port} ")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()
