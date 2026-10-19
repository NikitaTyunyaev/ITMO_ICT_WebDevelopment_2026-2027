import socket

HOST = '127.0.0.1'
PORT = 8080

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"UDP сервер запущен на {HOST}:{PORT}")
    print("Ожидание входящих сообщений...")

    try:
        while True:
            data, client_address = server_socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Получено сообщение от {client_address}: {message}")

            response = "Hello, client"
            server_socket.sendto(response.encode('utf-8'), client_address)
            print(f"Отправлен ответ клиенту {client_address}: {response}")
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    udp_server()
