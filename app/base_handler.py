import os
from http.server import BaseHTTPRequestHandler
import pathlib


STATIC_DIR = os.getenv("STATIC_DIR", "static")
STATIC_PATH = pathlib.Path(__file__).cwd().parent.resolve()/ STATIC_DIR

# в этом хэндлере должна быть описана логика работы сервера
class BaseHandler(BaseHTTPRequestHandler):
    server_version = "0.1"
    server_name = "Image Hosting"

    # html_response обрабатывает html запрос и выдает статус код ,и
    # проверяет, если data тип bytes, то читает файл иначе декодирует
    def response(self, data:str | bytes, content_type: str ="text/html", status_code=200) -> None:
        self.send_response(status_code)
        self.send_header("Content-type",content_type)
        self.end_headers()
        self.wfile.write(data if isinstance(data, bytes) else data.encode("utf-8"))

    def html_response(self, data:str | bytes, status_code=200) -> None:
        self.response(data, "text/html", status_code)


    #загруаем статические файлы и кодируем их в байты
    @staticmethod
    def load_static(filename:str) -> bytes:
        try:
            with open( STATIC_PATH/ filename, "rb") as f:
                return f.read()
        except FileNotFoundError:
            return b"Not Found"

    #объединяет html_response и load_static
    def template_response(self, template_filename:str) -> None:
        self.html_response(self.load_static(template_filename))

    def send_file(self, filename:str) -> None:
        if filename.endswith(".png"):
            content_type = "image/png"
        elif filename.endswith(".css"):
            content_type = "text/css"
        elif filename.endswith(".js"):
            content_type = "text/javascript"
        else:
            content_type = "application/octet-stream"
        self.response(self.load_static(filename),content_type)