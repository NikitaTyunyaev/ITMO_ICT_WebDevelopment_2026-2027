import datetime
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080

clients = {}  # socket -> nickname
chat_history = []  # list of strings
clients_lock = threading.Lock()
history_lock = threading.Lock()

def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")

def broadcast(message: str, sender_socket: socket.socket = None):
    formatted_msg = f"[{get_timestamp()}] {message}"
    print(formatted_msg)

    with history_lock:
        chat_history.append(formatted_msg)
        if len(chat_history) > 100:
            chat_history.pop(0)

    with clients_lock:
        broken_clients = []
        for client_sock in list(clients.keys()):
            if client_sock != sender_socket:
                try:
                    client_sock.sendall((formatted_msg + "\n").encode('utf-8'))
                except (ConnectionResetError, BrokenPipeError, socket.error):
                    broken_clients.append(client_sock)

        for broken_sock in broken_clients:
            remove_client(broken_sock)

def remove_client(client_socket: socket.socket):
    nickname = None
    with clients_lock:
        if client_socket in clients:
            nickname = clients.pop(client_socket)

    try:
        client_socket.close()
    except Exception:
        pass

    if nickname:
        broadcast(f"--- Пользователь '{nickname}' покинул чат ---")

def handle_client(client_socket: socket.socket, client_address):
    nickname = None
    try:
        client_socket.sendall("WELCOME: Пожалуйста, введите ваш никнейм:\n".encode('utf-8'))
        raw_name = client_socket.recv(1024).decode('utf-8').strip()

        if not raw_name:
            client_socket.sendall("ERR: Никнейм не может быть пустым.\n".encode('utf-8'))
            client_socket.close()
            return

        nickname = raw_name

        with clients_lock:
            clients[client_socket] = nickname

        print(f"[+] Подключен: '{nickname}' ({client_address})")

        # Отправляем историю чата новому пользователю
        with history_lock:
            if chat_history:
                client_socket.sendall("--- Последние сообщения в чате ---\n".encode('utf-8'))
                for old_msg in chat_history[-20:]:
                    client_socket.sendall((old_msg + "\n").encode('utf-8'))
                client_socket.sendall("----------------------------------\n".encode('utf-8'))

        broadcast(f"+++ Пользователь '{nickname}' присоединился к чату! +++", sender_socket=client_socket)
        client_socket.sendall(f"Добро пожаловать в чат, {nickname}! Для выхода введите /exit\n".encode('utf-8'))

        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            text = data.decode('utf-8').strip()
            if not text:
                continue

            if text.lower() in ('/exit', 'exit', '/quit', 'quit'):
                client_socket.sendall("BYE: Вы вышли из чата.\n".encode('utf-8'))
                break

            broadcast(f"[{nickname}]: {text}", sender_socket=client_socket)

    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print(f"Ошибка при работе с клиентом {client_address}: {e}")
    finally:
        remove_client(client_socket)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    print(f"TCP сервер чата запущен на {HOST}:{PORT}")
    print("Готов к одновременному обслуживанию множества клиентов.")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            client_thread.start()
    except KeyboardInterrupt:
        print("\nСервер чата останавливается...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
