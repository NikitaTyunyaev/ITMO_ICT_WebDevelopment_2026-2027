import math
import socket

HOST = '127.0.0.1'
PORT = 8080

def solve_quadratic(a: float, b: float, c: float) -> str:
    if a == 0:
        if b == 0:
            if c == 0:
                return "Уравнение вырождено в 0 = 0: бесконечно много решений."
            return f"Уравнение {c} = 0 не имеет решений."
        x = -c / b
        return f"Коэффициент a = 0 (линейное уравнение {b}x + {c} = 0). Корень: x = {x:.4f}"

    discriminant = b ** 2 - 4 * a * c

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        return (
            f"Дискриминант D = {discriminant:.4f} > 0.\n"
            f"Уравнение имеет два действительных корня:\n"
            f"x1 = {x1:.4f}\n"
            f"x2 = {x2:.4f}"
        )
    elif discriminant == 0:
        x = -b / (2 * a)
        return (
            f"Дискриминант D = 0.\n"
            f"Уравнение имеет один действительный корень (кратности 2):\n"
            f"x = {x:.4f}"
        )
    else:
        real_part = -b / (2 * a)
        imag_part = math.sqrt(-discriminant) / (2 * a)
        return (
            f"Дискриминант D = {discriminant:.4f} < 0.\n"
            f"Действительных корней нет. Комплексные корни:\n"
            f"x1 = {real_part:.4f} + {abs(imag_part):.4f}i\n"
            f"x2 = {real_part:.4f} - {abs(imag_part):.4f}i"
        )

def tcp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"TCP сервер вычислений (Вариант 2: Квадратное уравнение) запущен на {HOST}:{PORT}")
    print("Ожидание подключений клиентов...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Подключился клиент: {client_address}")

            data = client_socket.recv(1024).decode('utf-8').strip()
            print(f"Получены коэффициенты от клиента: '{data}'")

            try:
                parts = data.split()
                if len(parts) != 3:
                    response = "Ошибка: ожидалось ровно 3 коэффициента (a, b, c), разделенных пробелом."
                else:
                    a, b, c = map(float, parts)
                    response = solve_quadratic(a, b, c)
            except ValueError:
                response = "Ошибка: коэффициенты должны быть действительными числами."
            except Exception as e:
                response = f"Внутренняя ошибка вычислений: {e}"

            client_socket.sendall(response.encode('utf-8'))
            print(f"Результат отправлен клиенту {client_address}")
            client_socket.close()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    tcp_server()
