"""
Базовый обработчик HTTP-запросов.

Содержит общую логику работы сервера:
отправку ответов, загрузку файлов,
валидацию изображений и обработку multipart-данных.
"""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler  # заменить на threadhttp
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image
from multipart import MultipartParser, parse_options_header, MultipartPart

from app.settings import IMAGE_EXTENSIONS, STATIC_PATH, MAX_FILE_SIZE, MEDIA_PATH

logger = logging.getLogger(__name__)


# в этом хэндлере должна быть описана логика работы сервера
class BaseHandler(BaseHTTPRequestHandler):
    """
    Базовый класс обработчика запросов.

    Используется как родительский класс
    для всех обработчиков приложения.
    """

    server_version = "0.1"
    server_name = "Image Hosting Server"

    # html_response обрабатывает html запрос и выдает статус код ,и
    # проверяет, если data тип bytes, то читает файл иначе декодирует
    def response(self, data: str | bytes, content_type: str = "text/html", status_code=200) -> None:

        """
        Отправляет HTTP-ответ клиенту.

        Args:
            data (str | bytes): Данные ответа.
            content_type (str): Тип содержимого.
            status_code (int): HTTP-код ответа.
        """

        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(
            data if isinstance(data, bytes) else data.encode("utf-8"))

    def html_response(self, data: str | bytes, status_code=200) -> None:

        """
        Отправляет HTML-ответ клиенту.

        Args:
            data (str | bytes): HTML-контент.
            status_code (int): HTTP-код ответа.
        """

        self.response(data, "text/html", status_code)

    def json_response(self, data: dict | list | str | bytes,
                      status_code=200) -> None:

        """
        Отправляет JSON-ответ клиенту.

        Args:
            data (dict | list | str | bytes): Данные ответа.
            status_code (int): HTTP-код ответа.
        """

        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        self.response(data, "application/json", status_code)

    @staticmethod
    def load_file(filename: str, directory: Path = STATIC_PATH) -> bytes:

        """
        Загружает файл из указанной директории.

        Args:
            filename (str): Имя файла.
            directory (Path): Папка поиска.

        Returns:
            bytes: Содержимое файла.
        """

        try:
            file_path = (directory / filename.lstrip("/")).resolve()
            file_path.relative_to(directory.resolve())

            with open(file_path, "rb") as f:
                return f.read()
        except (FileNotFoundError, ValueError):
            return b"Not Found"

    def template_response(self, template_filename: str) -> None:

        """
        Отправляет HTML-шаблон клиенту.

        Args:
            template_filename (str): Имя шаблона.
        """

        self.html_response(self.load_file(template_filename))

    def send_static_file(self, filename: str) -> None:

        """
        Отправляет статический файл клиенту.

        Args:
            filename (str): Имя файла.
        """

        if filename.endswith(".png"):
            content_type = "image/png"
        elif filename.endswith(".css"):
            content_type = "text/css"
        elif filename.endswith(".js"):
            content_type = "text/javascript"
        else:
            content_type = "application/octet-stream"
        self.response(self.load_file(filename), content_type)

    def send_media_file(self, filename: str) -> None:

        """
        Отправляет изображение клиенту.

        Args:
            filename (str): Имя изображения.
        """

        self.response(self.load_file(filename, MEDIA_PATH), "image/png")

    def validate_file(self, file: MultipartPart) -> bool:

        """
        Проверяет корректность загружаемого файла.

        Проверяет расширение, размер файла
        и валидность изображения.

        Args:
            file (MultipartPart): Загружаемый файл.

        Returns:
            bool: Результат проверки.
        """

        if not file.filename:
            self.response("Filename is missing", status_code=400)
            return False

        if "." not in file.filename:
            self.response("File has no extension", status_code=400)
            return False

        name, ext = file.filename.rsplit(".", 1)  # сплит по последней точке, чтобы исключить имена "имя.имя.jpg"

        if ext.lower() not in IMAGE_EXTENSIONS:
            self.response(
                f"Invalid file type. Allowed types: {IMAGE_EXTENSIONS}",
                status_code=400
            )
            return False
        if file.size > MAX_FILE_SIZE:
            self.response('File too big', status_code=400)
            return False

        try:
            image = Image.open(BytesIO(file.raw))
            image.verify()

        except Exception as e:
            self.response(f"File is not a valid image. Exception {e}", status_code=400)
            return False

        return True

    def parse_multipart(self, content_type: str, options: dict,
                        content_length: int) -> dict | None:

        """
        Обрабатывает multipart-запрос.

        Сохраняет файл и формирует словарь
        с информацией об изображении.

        Args:
            content_type (str): Тип содержимого.
            options (dict): Параметры запроса.
            content_length (int): Размер запроса.

        Returns:
            dict | None: Информация о файле.
        """

        logger.info(content_type)
        logger.info(options)
        logger.info(self.headers["Content-Type"])

        if content_type == "multipart/form-data" and "boundary" in options:
            parser = MultipartParser(self.rfile,
                                     boundary=options["boundary"],
                                     content_length=content_length)

            for part in parser:
                if self.validate_file(part):
                    unique_name = str(uuid4())[:8]
                    logger.info(f"{part.filename}: File upload({part.size} bytes")
                    ext = Path(part.filename).suffix
                    uploaded_name = f'{unique_name}{ext}'
                    part.save_as(MEDIA_PATH / uploaded_name)

                    image_data = {
                        'filename': unique_name,
                        'original_name': part.filename,
                        'size': part.size,
                        'file_type': ext.lstrip('.')

                    }
                    return image_data

                else:
                    logger.info(
                        f"{part.name}: Invalid file ({part.size} bytes)")
                    return None

        return None

    def upload_file(self) -> str | None:
        content_type, options = parse_options_header(
            self.headers["Content-Type"])
        content_length = int(self.headers["Content-Length"])
        logger.info(self.headers["Content-Type"])
        logger.info(content_type)
        logger.info(options)
        return self.parse_multipart(content_type, options, content_length)
