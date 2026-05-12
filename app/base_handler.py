from __future__ import  annotations

import json
import logging

from http.server import BaseHTTPRequestHandler
from pathlib import Path
import logging
from multipart import MultipartParser, parse_options_header, MultipartPart


from app.settings import IMAGE_EXTENSIONS, STATIC_PATH, MEDIA_DIR, MAX_FILE_SIZE, MEDIA_PATH

logger = logging.getLogger(__name__)

# в этом хэндлере должна быть описана логика работы сервера
class BaseHandler(BaseHTTPRequestHandler):
    server_version = "0.1"
    server_name = "Image Hosting Server"

    # html_response обрабатывает html запрос и выдает статус код ,и
    # проверяет, если data тип bytes, то читает файл иначе декодирует
    def response(self, data:str | bytes, content_type: str ="text/html", status_code=200)-> None:
        self.send_response(status_code)
        self.send_header("Content-type",content_type)
        self.end_headers()
        self.wfile.write(data if isinstance(data, bytes) else data.encode("utf-8"))

    def html_response(self, data:str | bytes, status_code=200) -> None:
        self.response(data, "text/html", status_code)

    def json_response(self, data: dict| list | str | bytes, status_code=200) -> None:
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        self.response(data, "application/json", status_code)

    #загруаем статические файлы и кодируем их в байты
    @staticmethod
    def load_static(filename:str) -> bytes:
        try:
            file_path = STATIC_PATH / filename.lstrip("/")
            with open( file_path, "rb") as f:
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



    def validate_file(self, file: MultipartPart) -> bool:
        name, ext = file.filename.split(".")
        if ext.lower() not in IMAGE_EXTENSIONS:
            self.response(f"Invalid file type. Allowed types: {IMAGE_EXTENSIONS}", status_code = 400)
            return False
        if file.size > MAX_FILE_SIZE:
            self.response('File too big', status_code = 400)
            return False
        return True


    def parse_multipart(self, content_type: str, options:dict,
                         content_length: int, filename: str = None) ->None:
                                                                                    #проработать логику, что можно загрузить только один файл за раз
        if content_type == "multipart/form-data" and "boundary" in options:
            parser = MultipartParser(self.rfile,boundary = options["boundary"],content_length = content_length)

            for part in parser:
                if self.validate_file(part):
                    logger.info(f"{part.name}: File upload({part.size} bytes")
                    part.save_as(MEDIA_PATH / (f"{filename}.{part.filename.split(".")[1]}" or part.filename))
                else:
                    logger.info(f"{part.name}: Invalid file({part.size} bytes)")

            for part in parser.parts():
                part.close()
        else:
            self.response(" Request w/out Form", 400)
            return
        self.response(" File uploaded successfully", 201)


    def upload_file(self, filename: str = None) -> None:
        content_type, options = parse_options_header(
            self.headers["Content-Type"])
        content_length = int(self.headers["Content-Length"])
        self.parse_multipart(content_type, options, content_length, filename)

