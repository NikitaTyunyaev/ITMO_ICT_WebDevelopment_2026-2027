import socket

HOST = '127.0.0.1'
PORT = 8080

def udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5.0)

    try:
        message = "Hello, server"
        print(f"Отправка сообщения серверу ({HOST}:{PORT}): {message}")
        client_socket.sendto(message.encode('utf-8'), (HOST, PORT))

        response, server_address = client_socket.recvfrom(1024)
        print(f"Ответ от сервера ({server_address}): {response.decode('utf-8')}")
    except socket.timeout:
        print("Таймаут ожидания ответа от сервера.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    udp_client()
