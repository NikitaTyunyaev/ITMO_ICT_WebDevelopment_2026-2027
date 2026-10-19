import socket

HOST = '127.0.0.1'
PORT = 8080

def get_float(prompt: str) -> float:
    while True:
        try:
            val_str = input(prompt).strip()
            return float(val_str)
        except ValueError:
            print("Ошибка ввода! Введите корректное число (например, 1, -2.5, 4).")

def tcp_client():
    print("=== Решение квадратного уравнения: ax^2 + bx + c = 0 ===")
    print("Введите коэффициенты уравнения:")
    a = get_float("Коэффициент a: ")
    b = get_float("Коэффициент b: ")
    c = get_float("Коэффициент c: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10.0)

    try:
        client_socket.connect((HOST, PORT))
        payload = f"{a} {b} {c}"
        print(f"\nОтправка коэффициентов на сервер ({HOST}:{PORT}): {payload}")
        client_socket.sendall(payload.encode('utf-8'))

        response = client_socket.recv(2048).decode('utf-8')
        print(f"\n--- Результат от сервера ---\n{response}")
    except socket.timeout:
        print("Ошибка: таймаут ожидания ответа от сервера.")
    except ConnectionRefusedError:
        print(f"Ошибка: не удалось подключиться к серверу по адресу {HOST}:{PORT}. Проверьте, запущен ли сервер.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    tcp_client()
