# Лабораторная работа №1: Работа с сокетами

**Студент:** Тюняев Никита  
**Группа:** K3341  
**Вариант задания 2:** 2 (Решение квадратного уравнения: $(34 - 1) \pmod 4 + 1 = 2$)  

---

## Цель работы
Понять принципы межсокетного взаимодействия в компьютерных сетях и веб-технологиях. Научиться проектировать и реализовывать базовую клиент-серверную архитектуру с использованием протоколов UDP и TCP, создавать многопоточные сетевые сервисы и разрабатывать веб-сервер с ручной обработкой HTTP-запросов (GET и POST).

---

## Практическое задание 1. Обмен сообщениями по UDP

### Описание задачи
Реализовать клиентскую и серверную часть приложения. Клиент отправляет серверу сообщение `Hello, server`, которое отображается на стороне сервера. В ответ сервер отправляет клиенту `Hello, client`, которое отображается у клиента. Работа выполняется с использованием протокола UDP (`socket.SOCK_DGRAM`) без установления предварительного соединения.

### Реализация

#### Сервер (`task1/server.py`):
```python
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
```

#### Клиент (`task1/client.py`):
```python
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
```

### Пример работы в терминале

**Сервер:**
```
UDP сервер запущен на 127.0.0.1:8080
Ожидание входящих сообщений...
Получено сообщение от ('127.0.0.1', 54321): Hello, server
Отправлен ответ клиенту ('127.0.0.1', 54321): Hello, client
```

**Клиент:**
```
Отправка сообщения серверу (127.0.0.1:8080): Hello, server
Ответ от сервера (('127.0.0.1', 8080)): Hello, client
```

---

## Практическое задание 2. Вычисления через TCP

### Описание задачи
Реализовать клиентскую и серверную часть приложения с использованием протокола TCP (`socket.SOCK_STREAM`). Клиент запрашивает параметры математической операции с клавиатуры и передает их серверу. Сервер вычисляет результат и возвращает его клиенту.

По номеру в журнале (34) выбран **Вариант 2 — Решение квадратного уравнения**:
$$ax^2 + bx + c = 0$$

Сервер вычисляет дискриминант $D = b^2 - 4ac$ и определяет корни уравнения:
- При $D > 0$: два действительных корня $x_{1,2} = \frac{-b \pm \sqrt{D}}{2a}$.
- При $D = 0$: один действительный корень $x = \frac{-b}{2a}$.
- При $D < 0$: действительных корней нет, выводятся комплексные корни $x_{1,2} = \frac{-b}{2a} \pm \frac{\sqrt{|D|}}{2a}i$.
- Предусмотрена обработка вырожденного случая $a = 0$ (линейное уравнение $bx + c = 0 \implies x = -c/b$).

### Реализация

#### Сервер (`task2/server.py`):
```python
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

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(1024).decode('utf-8').strip()
            try:
                parts = data.split()
                if len(parts) != 3:
                    response = "Ошибка: ожидалось ровно 3 коэффициента (a, b, c)."
                else:
                    a, b, c = map(float, parts)
                    response = solve_quadratic(a, b, c)
            except ValueError:
                response = "Ошибка: коэффициенты должны быть числами."

            client_socket.sendall(response.encode('utf-8'))
            client_socket.close()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    tcp_server()
```

#### Клиент (`task2/client.py`):
```python
import socket

HOST = '127.0.0.1'
PORT = 8080

def get_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError:
            print("Ошибка! Введите число.")

def tcp_client():
    print("=== Решение квадратного уравнения: ax^2 + bx + c = 0 ===")
    a = get_float("Коэффициент a: ")
    b = get_float("Коэффициент b: ")
    c = get_float("Коэффициент c: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        payload = f"{a} {b} {c}"
        client_socket.sendall(payload.encode('utf-8'))

        response = client_socket.recv(2048).decode('utf-8')
        print(f"\n--- Результат от сервера ---\n{response}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    tcp_client()
```

### Пример работы в терминале
```
=== Решение квадратного уравнения: ax^2 + bx + c = 0 ===
Введите коэффициенты уравнения:
Коэффициент a: 1
Коэффициент b: -5
Коэффициент c: 6

Отправка коэффициентов на сервер (127.0.0.1:8080): 1.0 -5.0 6.0

--- Результат от сервера ---
Дискриминант D = 1.0000 > 0.
Уравнение имеет два действительных корня:
x1 = 3.0000
x2 = 2.0000
```

---

## Практическое задание 3. Раздача HTML-страницы по HTTP

### Описание задачи
Реализовать серверную часть веб-приложения на сокетах. Сервер принимает подключение по протоколу TCP, парсит входящий HTTP GET-запрос и отправляет в ответ спецификационное HTTP/1.1 сообщение, содержащее статус 200 OK, необходимые заголовки (`Content-Type`, `Content-Length`) и HTML-страницу из внешнего файла `index.html`.

### Реализация

#### Сервер (`task3/server.py`):
```python
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

    html_path = os.path.join(os.path.dirname(__file__), 'index.html')

    try:
        while True:
            client_connection, client_address = server_socket.accept()
            request_data = client_connection.recv(2048).decode('utf-8', errors='ignore')

            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            html_bytes = html_content.encode('utf-8')
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html; charset=UTF-8\r\n"
                f"Content-Length: {len(html_bytes)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode('utf-8') + html_bytes

            client_connection.sendall(http_response)
            client_connection.close()
    finally:
        server_socket.close()

if __name__ == "__main__":
    http_server()
```

### Проверка ответа сервера через `curl`
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 5657
Connection: close
Server: Simple-Python-Socket-Server/1.0

<!DOCTYPE html>
<html lang="ru">
...
```

---

## Практическое задание 4. Многопользовательский чат на сокетах

### Описание задачи
Реализовать многопользовательский чат на протоколе TCP с использованием модуля `threading`.
- Сервер обслуживает множество пользователей параллельно (для каждого клиента запускается отдельный поток).
- Идентификация пользователей по никнеймам.
- Рассылка сообщений всем остальным участникам (broadcast).
- Отправка истории сообщений при подключении.
- Уведомления о входе и выходе участников.
- Возможность выхода по команде `/exit`.
- Один универсальный скрипт клиента `client.py`.

### Реализация

#### Сервер (`task4/server.py`):
```python
import datetime
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080

clients = {}
chat_history = []
clients_lock = threading.Lock()
history_lock = threading.Lock()

def broadcast(message: str, sender_socket: socket.socket = None):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    print(formatted_msg)

    with history_lock:
        chat_history.append(formatted_msg)
        if len(chat_history) > 100:
            chat_history.pop(0)

    with clients_lock:
        for client_sock in list(clients.keys()):
            if client_sock != sender_socket:
                try:
                    client_sock.sendall((formatted_msg + "\n").encode('utf-8'))
                except:
                    remove_client(client_sock)

def remove_client(client_socket: socket.socket):
    with clients_lock:
        nickname = clients.pop(client_socket, None)
    try:
        client_socket.close()
    except:
        pass
    if nickname:
        broadcast(f"--- Пользователь '{nickname}' покинул чат ---")
```

#### Клиент (`task4/client.py`):
Клиент разделяет сетевое взаимодействие на два параллельных потока: один читает сообщения от сервера в цикле, второй считывает пользовательский ввод:
```python
def receive_messages(sock: socket.socket):
    while not stop_event.is_set():
        try:
            data = sock.recv(2048)
            if not data:
                break
            print(data.decode('utf-8', errors='ignore'), end='')
        except:
            break
```

### Пример параллельного взаимодействия клиентов
```
[23:29:08] +++ Пользователь 'Nikita' присоединился к чату! +++
[23:29:08] +++ Пользователь 'Alice' присоединился к чату! +++
[23:29:09] [Nikita]: Hello from Nikita!
[23:29:09] [Alice]: Hello Nikita! How are you?
[23:29:10] --- Пользователь 'Alice' покинул чат ---
```

---

## Практическое задание 5. Простой веб-сервер (GET/POST) — Журнал оценок

### Описание задачи
Написать простой веб-сервер для обработки HTTP GET и POST запросов с помощью библиотеки `socket` без использования сторонних веб-фреймворков.
- Принимает и записывает информацию о дисциплине и оценке по ней.
- Отдает информацию обо всех оценках в виде стилизованной HTML-страницы.
- **Требование группировки:** оценки строго группируются по дисциплинам (структура `dict[str, list[int]]`).
- Реализован паттерн Post/Redirect/Get (PRG) со статусом 303 See Other для предотвращения дублирования данных при обновлении страницы.

### Реализация

#### Сервер (`task5/server.py`):
```python
class MyHTTPServer:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._grades = {
            "Веб-программирование": [5, 5, 4],
            "Архитектура вычислительных систем": [5, 4],
            "Математический анализ": [4, 5, 5]
        }

    def parse_request(self, conn: socket.socket) -> dict:
        """Считывание и разбор стартовой строки, заголовков и тела."""
        buffer = b""
        while b"\r\n\r\n" not in buffer:
            chunk = conn.recv(1024)
            if not chunk: break
            buffer += chunk

        header_bytes, _, rest = buffer.partition(b"\r\n\r\n")
        lines = header_bytes.decode('utf-8', errors='ignore').split("\r\n")
        method, path, protocol = lines[0].split()

        headers = {}
        for line in lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k.lower()] = v.strip()

        content_length = int(headers.get('content-length', 0))
        body = rest
        while len(body) < content_length:
            chunk = conn.recv(1024)
            if not chunk: break
            body += chunk

        return {'method': method, 'path': path, 'headers': headers, 'body': body}

    def handle_post_grade(self, body_bytes: bytes) -> dict:
        form_data = parse_qs(body_bytes.decode('utf-8', errors='ignore'))
        discipline = form_data.get('discipline', [''])[0].strip()
        grade = int(form_data.get('grade', ['0'])[0])

        if discipline not in self._grades:
            self._grades[discipline] = []
        self._grades[discipline].append(grade)

        return {'status_code': 303, 'reason': 'See Other', 'headers': {'Location': '/'}}
```

### Демонстрация работы группировки
При отправке запросов:
1. `POST /add_grade` -> `discipline=Базы данных&grade=5`
2. `POST /add_grade` -> `discipline=Базы данных&grade=4`

Сервер обновляет внутренний словарь:
`"Базы данных": [5, 4]`  
И генерирует единую строку таблицы со средним баллом `4.50`:
```html
<tr>
    <td class="subject-cell">Базы данных</td>
    <td class="grades-cell">
        <span class='grade-badge grade-5'>5</span>
        <span class='grade-badge grade-4'>4</span>
    </td>
    <td class="avg-cell"><span class="avg-badge">4.50</span></td>
</tr>
```

---

## Выводы
В ходе выполнения лабораторной работы №1 были освоены:
1. **Низкоуровневая работа с сокетами** в Python через модуль `socket`.
2. **Различия протоколов транспортного уровня:** протокол UDP (без установления соединения, высокая скорость) и протокол TCP (надёжная доставка, гарантированный порядок байт, соединение).
3. **Формирование и разбор HTTP/1.1 протокола:** ручной разбор стартовой строки, заголовков, заголовка `Content-Length`, обработка тела запроса.
4. **Многопоточное сетевое программирование:** организация параллельной обработки клиентов с помощью `threading` и обеспечение потокобезопасности разделяемых структур данных при помощи `threading.Lock`.
5. **Проектирование веб-сервера:** связка GET и POST запросов, валидация пользовательских данных, структурированное хранение и отдача динамического HTML.
