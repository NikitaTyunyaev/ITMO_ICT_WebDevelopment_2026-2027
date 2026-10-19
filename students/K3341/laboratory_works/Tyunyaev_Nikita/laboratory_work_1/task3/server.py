import os
import socket

HOST = '127.0.0.1'
PORT = 8080

def http_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"HTTP сервер запущен на http://{HOST}:{PORT}/")
    print("Откройте этот адрес в веб-браузере для просмотра страницы.")

    html_path = os.path.join(os.path.dirname(__file__), 'index.html')

    try:
        while True:
            client_connection, client_address = server_socket.accept()
            print(f"\n[+] Новое подключение от: {client_address}")

            request_data = client_connection.recv(2048).decode('utf-8', errors='ignore')
            request_line = request_data.split('\r\n')[0] if request_data else "EMPTY"
            print(f"Запрос: {request_line}")

            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except FileNotFoundError:
                html_content = "<h1>404 Not Found: index.html not found</h1>"

            html_bytes = html_content.encode('utf-8')

            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(html_bytes)}\r\n"
                "Connection: close\r\n"
                "Server: Simple-Python-Socket-Server/1.0\r\n"
                "\r\n"
            ).encode('utf-8') + html_bytes

            client_connection.sendall(http_response)
            client_connection.close()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    http_server()
