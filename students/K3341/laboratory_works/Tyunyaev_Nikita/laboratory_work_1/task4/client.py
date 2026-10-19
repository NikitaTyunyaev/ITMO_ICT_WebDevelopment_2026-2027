import socket
import sys
import threading

HOST = '127.0.0.1'
PORT = 8080

stop_event = threading.Event()

def receive_messages(sock: socket.socket):
    while not stop_event.is_set():
        try:
            data = sock.recv(2048)
            if not data:
                if not stop_event.is_set():
                    print("\n[Соединение с сервером разорвано]")
                stop_event.set()
                break
            print(data.decode('utf-8', errors='ignore'), end='')
        except (socket.error, OSError):
            if not stop_event.is_set():
                print("\n[Ошибка чтения из сокета]")
            stop_event.set()
            break

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Не удалось подключиться к серверу по адресу {HOST}:{PORT}. Проверьте, что сервер запущен.")
        return

    # Получаем приветствие от сервера с запросом имени
    welcome_prompt = client_socket.recv(1024).decode('utf-8')
    print(welcome_prompt, end='')

    nickname = ""
    while not nickname:
        nickname = input().strip()

    client_socket.sendall((nickname + "\n").encode('utf-8'))

    # Запускаем поток прослушивания входящих сообщений
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    recv_thread.start()

    try:
        while not stop_event.is_set():
            msg = input()
            if stop_event.is_set():
                break

            if msg.strip().lower() in ('/exit', 'exit', '/quit', 'quit'):
                try:
                    client_socket.sendall("/exit\n".encode('utf-8'))
                except Exception:
                    pass
                stop_event.set()
                break

            if msg.strip():
                try:
                    client_socket.sendall((msg + "\n").encode('utf-8'))
                except Exception:
                    print("[Ошибка отправки сообщения]")
                    break
    except (KeyboardInterrupt, EOFError):
        print("\nЗавершение работы клиента...")
        try:
            client_socket.sendall("/exit\n".encode('utf-8'))
        except Exception:
            pass
        stop_event.set()
    finally:
        client_socket.close()
        print("Вы отключены от чата.")

if __name__ == "__main__":
    start_client()
