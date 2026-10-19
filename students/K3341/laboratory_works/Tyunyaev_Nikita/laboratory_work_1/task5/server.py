import html
import socket
from urllib.parse import parse_qs, unquote_plus

HOST = '127.0.0.1'
PORT = 8080

class MyHTTPServer:
    def __init__(self, host: str, port: int, server_name: str = "GradeSocketServer/1.0"):
        self._host = host
        self._port = port
        self._server_name = server_name
        # Структура данных: словарь {Название_дисциплины: [список оценок]}
        self._grades = {
            "Веб-программирование": [5, 5, 4],
            "Архитектура вычислительных систем": [5, 4],
            "Математический анализ": [4, 5, 5]
        }

    def serve_forever(self):
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen(10)
            print(f"Сервер журнала оценок запущен на http://{self._host}:{self._port}/")
            print("Для остановки нажмите Ctrl+C")

            while True:
                client_sock, client_addr = serv_sock.accept()
                try:
                    self.serve_client(client_sock)
                except Exception as e:
                    print(f"Ошибка при обработке запроса от {client_addr}: {e}")
        except KeyboardInterrupt:
            print("\nСервер успешно остановлен.")
        finally:
            serv_sock.close()

    def serve_client(self, conn: socket.socket):
        try:
            req = self.parse_request(conn)
            if req:
                resp = self.handle_request(req)
                self.send_response(conn, resp)
        finally:
            conn.close()

    def parse_request(self, conn: socket.socket) -> dict:
        """Считывание и разбор стартовой строки, заголовков и тела запроса."""
        conn.settimeout(3.0)
        buffer = b""

        while b"\r\n\r\n" not in buffer:
            chunk = conn.recv(1024)
            if not chunk:
                break
            buffer += chunk

        if not buffer:
            return None

        header_bytes, _, rest = buffer.partition(b"\r\n\r\n")
        header_text = header_bytes.decode('utf-8', errors='ignore')
        lines = header_text.split("\r\n")

        if not lines:
            return None

        # Разбор стартовой строки: МЕТОД URL ПРОТОКОЛ
        request_line_parts = lines[0].split()
        if len(request_line_parts) != 3:
            return None

        method, path, protocol = request_line_parts

        headers = {}
        for line in lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k.lower()] = v.strip()

        # Если метод POST, считываем тело в соответствии с Content-Length
        body = rest
        content_length = int(headers.get('content-length', 0))

        while len(body) < content_length:
            chunk = conn.recv(1024)
            if not chunk:
                break
            body += chunk

        return {
            'method': method.upper(),
            'path': path,
            'protocol': protocol,
            'headers': headers,
            'body': body
        }

    def handle_request(self, req: dict) -> dict:
        """Маршрутизация и обработка GET/POST запросов."""
        method = req['method']
        path = req['path'].split('?')[0]  # отсекаем query params для пути

        if method == 'GET' and path in ('/', '/index.html'):
            return self.handle_get_index()
        elif method == 'POST' and path in ('/', '/add_grade'):
            return self.handle_post_grade(req['body'])
        else:
            return self.handle_404()

    def handle_get_index(self) -> dict:
        """Формирование HTML-страницы с формой и сгруппированным журналом оценок."""
        content = self.render_html()
        body_bytes = content.encode('utf-8')

        return {
            'status_code': 200,
            'reason': 'OK',
            'headers': {
                'Content-Type': 'text/html; charset=UTF-8',
                'Content-Length': str(len(body_bytes)),
                'Server': self._server_name,
                'Connection': 'close'
            },
            'body': body_bytes
        }

    def handle_post_grade(self, body_bytes: bytes) -> dict:
        """Обработка добавления дисциплины и оценки."""
        try:
            body_str = body_bytes.decode('utf-8', errors='ignore')
            form_data = parse_qs(body_str)

            discipline = form_data.get('discipline', [''])[0].strip()
            grade_str = form_data.get('grade', [''])[0].strip()

            if not discipline:
                return self.handle_bad_request("Название дисциплины не может быть пустым.")

            grade = int(grade_str)
            if grade < 1 or grade > 5:
                return self.handle_bad_request("Оценка должна быть целым числом в диапазоне от 1 до 5.")

            # Сохранение с группировкой по дисциплине
            if discipline not in self._grades:
                self._grades[discipline] = []
            self._grades[discipline].append(grade)

            print(f"[+] Добавлена оценка: {discipline} -> {grade}. Текущий список: {self._grades[discipline]}")

            # Редирект Post/Redirect/Get на корень
            return {
                'status_code': 303,
                'reason': 'See Other',
                'headers': {
                    'Location': '/',
                    'Server': self._server_name,
                    'Connection': 'close'
                },
                'body': b""
            }

        except (ValueError, KeyError):
            return self.handle_bad_request("Некорректный формат переданных данных формы.")

    def handle_404(self) -> dict:
        html_404 = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>404 Not Found</title></head>"
            "<body style='font-family: sans-serif; text-align: center; padding-top: 50px; background:#0f172a; color:#f8fafc;'>"
            "<h1>404 — Страница не найдена</h1><p><a href='/' style='color:#38bdf8;'>Вернуться к журналу</a></p>"
            "</body></html>"
        )
        body_bytes = html_404.encode('utf-8')
        return {
            'status_code': 404,
            'reason': 'Not Found',
            'headers': {
                'Content-Type': 'text/html; charset=UTF-8',
                'Content-Length': str(len(body_bytes)),
                'Server': self._server_name,
                'Connection': 'close'
            },
            'body': body_bytes
        }

    def handle_bad_request(self, message: str) -> dict:
        html_400 = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>400 Bad Request</title></head>"
            f"<body style='font-family: sans-serif; text-align: center; padding-top: 50px; background:#0f172a; color:#f8fafc;'>"
            f"<h1>Ошибка 400: Неверный запрос</h1><p>{html.escape(message)}</p>"
            f"<p><a href='/' style='color:#38bdf8;'>Назад к форме</a></p></body></html>"
        )
        body_bytes = html_400.encode('utf-8')
        return {
            'status_code': 400,
            'reason': 'Bad Request',
            'headers': {
                'Content-Type': 'text/html; charset=UTF-8',
                'Content-Length': str(len(body_bytes)),
                'Server': self._server_name,
                'Connection': 'close'
            },
            'body': body_bytes
        }

    def render_html(self) -> str:
        """Генерация адаптивного HTML-интерфейса журнала оценок."""
        rows_html = ""
        total_grades_count = 0
        total_grades_sum = 0

        for subject, grades_list in self._grades.items():
            avg_grade = sum(grades_list) / len(grades_list) if grades_list else 0.0
            total_grades_count += len(grades_list)
            total_grades_sum += sum(grades_list)

            # Бейджи для оценок
            badges = " ".join([
                f"<span class='grade-badge grade-{g}'>{g}</span>" for g in grades_list
            ])

            rows_html += f"""
            <tr>
                <td class="subject-cell">{html.escape(subject)}</td>
                <td class="grades-cell">{badges}</td>
                <td class="avg-cell"><span class="avg-badge">{avg_grade:.2f}</span></td>
            </tr>
            """

        overall_avg = (total_grades_sum / total_grades_count) if total_grades_count > 0 else 0.0

        if not rows_html:
            rows_html = "<tr><td colspan='3' style='text-align:center; color:#94a3b8; padding:20px;'>Оценок пока нет. Добавьте первую!</td></tr>"

        return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Электронный журнал оценок | Тюняев Никита K3341</title>
    <style>
        :root {{
            --bg: #0b1120;
            --surface: #1e293b;
            --surface-hover: #334155;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --accent: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
            padding: 30px 16px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 32px;
        }}

        .badge-header {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 12px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}

        h1 {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 6px;
        }}

        p.author {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 24px;
            margin-bottom: 32px;
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4);
        }}

        .card-title {{
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 18px;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .form-group {{
            margin-bottom: 16px;
        }}

        label {{
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        input[type="text"], select {{
            width: 100%;
            padding: 10px 14px;
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 8px;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        input[type="text"]:focus, select:focus {{
            border-color: var(--accent);
        }}

        button[type="submit"] {{
            width: 100%;
            padding: 12px;
            background: var(--primary);
            color: white;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
        }}

        button[type="submit"]:hover {{
            background: var(--primary-hover);
        }}

        button[type="submit"]:active {{
            transform: scale(0.98);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th {{
            background: #0f172a;
            color: var(--text-muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 12px 14px;
            border-bottom: 2px solid var(--border);
        }}

        td {{
            padding: 14px;
            border-bottom: 1px solid var(--border);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        .subject-cell {{
            font-weight: 600;
            color: #f1f5f9;
        }}

        .grade-badge {{
            display: inline-block;
            width: 28px;
            height: 28px;
            line-height: 28px;
            text-align: center;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            margin: 2px;
        }}

        .grade-5 {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }}
        .grade-4 {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
        .grade-3 {{ background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4); }}
        .grade-2 {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}
        .grade-1 {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.4); }}

        .avg-badge {{
            background: #0f172a;
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--accent);
        }}

        .stat-banner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 20px;
            margin-top: 16px;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .stat-banner strong {{
            color: #ffffff;
            font-size: 1.1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="badge-header">ЛР1 • Задание 5 • HTTP GET & POST</span>
            <h1>Электронный журнал оценок</h1>
            <p class="author">Студент: Тюняев Никита | Группа: K3341 | Стек: Python socket (чистый TCP)</p>
        </header>

        <div class="grid">
            <div class="card">
                <h2 class="card-title">Добавить оценку</h2>
                <form action="/add_grade" method="POST">
                    <div class="form-group">
                        <label for="discipline">Название дисциплины</label>
                        <input type="text" id="discipline" name="discipline" placeholder="Например: Сети и протоколы" required>
                    </div>
                    <div class="form-group">
                        <label for="grade">Оценка</label>
                        <select id="grade" name="grade" required>
                            <option value="5">5 (Отлично)</option>
                            <option value="4">4 (Хорошо)</option>
                            <option value="3">3 (Удовлетворительно)</option>
                            <option value="2">2 (Неудовлетворительно)</option>
                            <option value="1">1 (Плохо)</option>
                        </select>
                    </div>
                    <button type="submit">Сохранить запись</button>
                </form>
            </div>

            <div class="card">
                <div class="card-title">
                    <span>Сводная ведомость</span>
                    <span style="font-size: 0.85rem; font-weight: normal; color: var(--text-muted);">Группировка по предмету</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Дисциплина</th>
                            <th>Оценки</th>
                            <th>Средний балл</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>

                <div class="stat-banner">
                    <span>Всего предметов: <strong>{len(self._grades)}</strong></span>
                    <span>Всего оценок: <strong>{total_grades_count}</strong></span>
                    <span>Общий средний балл: <strong>{overall_avg:.2f}</strong></span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

    def send_response(self, conn: socket.socket, resp: dict):
        """Формирование и отправка HTTP-ответа."""
        status_line = f"HTTP/1.1 {resp['status_code']} {resp['reason']}\r\n"
        headers_str = "".join([f"{k}: {v}\r\n" for k, v in resp.get('headers', {}).items()])
        head_bytes = (status_line + headers_str + "\r\n").encode('utf-8')

        conn.sendall(head_bytes + resp.get('body', b""))

if __name__ == "__main__":
    server = MyHTTPServer(HOST, PORT)
    server.serve_forever()
