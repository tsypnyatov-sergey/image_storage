import os
from http.server import BaseHTTPRequestHandler



STATIC_DIR = os.getenv("STATIC_DIR", "static")

# в этом хэндлере должна быть описана логика работы сервера
class BaseHandler(BaseHTTPRequestHandler):
    server_version = "0.1"
    server_name = "Image Hosting"

    # html_response обрабатывает html запрос и выдает статус код ,и
    # проверяет, если data тип bytes, то читает файл иначе декодирует
    def html_response(self, data:str | bytes, status_code=200) -> None:
        self.send_response(status_code)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(data if isinstance(data, bytes) else data.encode("utf-8"))


    #загруаем статические файлы и кодируем их в байты
    def load_static(self, filename:str) -> bytes:
        try:
            with open(filename, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return b"Not Found"

    #объединяет html_response и load_static
    def template_response(self, template_filename:str) -> None:
        self.html_response(self.load_static(template_filename))