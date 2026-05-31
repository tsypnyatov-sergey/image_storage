"""
Модуль для работы с базой данных PostgreSQL.
"""

import logging
import os
from math import ceil
from typing import Optional, Any

from dotenv import load_dotenv
from psycopg import Connection, connect, ProgrammingError, OperationalError
from psycopg.abc import Params
from psycopg.rows import tuple_row

from app.queries import ADD_IMAGE, GET_IMAGES_NAMES, DELETE_IMAGE_BY_NAME, \
    GET_ALL_IMAGES, CREATE_TABLE, GET_IMAGES_COUNT
from app.settings import IMAGE_LIMIT

load_dotenv()
DB = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'dbname': os.getenv('POSTGRES_DB'),
}

DSN = f"postgresql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['dbname']}"
logger = logging.getLogger(__name__)


class DBManager:
    """
    Класс для выполнения запросов к базе данных.
    """

    def __init__(self, db_config: dict = None, row_factory=tuple_row):
        """
        Создает объект подключения к базе данных.
        """

        self.db_config = db_config or DB
        self.dsn = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']}"
        self._connection: Optional[Connection] = None
        self.row_factory = row_factory

        # self.init_tables()

    def _execute(self, query, data: Params = None, fetch: bool = True,
                 fetch_all: bool = True) -> list | None:
        """
        Выполняет SQL-запрос.

        Args:
            query: SQL-запрос.
            data: Параметры запроса.

        Returns:
            list | None: Результат выполнения.
        """

        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, data)
                    if fetch:
                        result = cur.fetchall() if fetch_all else cur.fetchone()
                        return result
            self._connection = None
        except OperationalError as e:
            print(f"Не удалось подключиться к базе данных:\n{e}")
        except ProgrammingError as e:
            print(f"Ошибка в SQL-запросе:\n{e}")

    def _connect(self) -> Optional[Connection]:
        """
        Создает подключение к базе данных.

        Returns:
            Connection: Подключение PostgreSQL.
        """

        return self._connection if self._connection else connect(self.dsn,
                                                                 row_factory=self.row_factory)

    def fetch_all(self, query, data: Params = None) -> list | None:
        """
        Получает все записи по запросу.
        """

        return self._execute(query, data)

    def fetch_one(self, query, data: Params = None) -> Any:
        """
        Получает одну запись по запросу.
        """
        return self._execute(query, data, fetch_all=False)[0]

    def execute(self, query, data: Params = None) -> list | None:
        """
        Выполняет запрос без возврата результата.
        """

        return self._execute(query, data, fetch=False, fetch_all=False)

    def add_image(self, image: dict):
        """
        Добавляет информацию об изображении в базу.

        Args:
            image (dict): Данные изображения.
        """

        self.execute(ADD_IMAGE, image)

    def get_images_names(self):
        """
        Получает список имен изображений.
        """

        return self.fetch_all(GET_IMAGES_NAMES)

    def get_images(self, page: int):
        """
        Получает изображения для указанной страницы.

        Args:
            page (int): Номер страницы.
        """

        offset = (page - 1) * IMAGE_LIMIT
        logger.info(f"offset: {offset}")
        return self.fetch_all(GET_ALL_IMAGES, (offset,))

    def delete_image(self, name):
        """
        Удаляет запись об изображении.

        Args:
            name (str): Имя файла.
        """

        self.execute(DELETE_IMAGE_BY_NAME, (name,))

    def init_tables(self):
        """
        Создает таблицы базы данных.
        """

        self.execute(CREATE_TABLE)

    def has_next(self, page):
        """
        Проверяет наличие следующей страницы.

        Args:
            page (int): Текущая страница.

        Returns:
            bool: Есть ли следующая страница.
        """

        images_count = self.fetch_one(GET_IMAGES_COUNT)
        return ceil(images_count / IMAGE_LIMIT) > page
