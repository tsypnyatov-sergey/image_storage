FROM python:3.12-alpine

WORKDIR /app


RUN POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install poetry

COPY pyproject.toml .

RUN poetry install

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]