# Image Storage 

Сервис где можно загружать картинки и получать ссылки. 

## Как запустить

### Через Docker 
```bash
docker compose up --build
```

Открой в браузере:
- http://localhost - главная
- http://localhost/upload - загрузить картинку
- http://localhost/images - смотреть все картинки

### Локально 
```bash
pip install -r requirements.txt
# создай .env файл
python -m app.main
# запусти Nginx отдельно если нужно
```

##  Что где лежит

```
image_storage/
├── app/                          # Python код (Backend)
│   ├── main.py                   # Запускает сервер
│   ├── image_hosting_handler.py  # Обрабатывает запросы
│   ├── base_handler.py           # Общие функции
│   ├── db_manager.py             # Работает с базой
│   ├── QUERIES.py                # SQL запросы
│   └── settings.py               # Конфиг
│
├── static/                       # HTML, CSS, JS (Frontend)
│   ├── index.html
│   ├── upload.html
│   ├── images.html
│   └── image-uploader/
│       ├── css/
│       └── img/
│       └── js/
│
├── images/                       # Папка с картинками (создается сама)
├── logs/                         # Логи 
├── docker-compose.yml            # Конфиг Docker
├── nginx.conf                    # Конфиг Nginx
├── Dockerfile                    # Как собрать контейнер
├── pyproject.toml                # Какие библиотеки нужны
└── .env.example                  # Пример переменных окружения
```

##  Конфигурация

Создай `.env` файл (скопируй из `.env.example`):

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=images_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## Что можно делать

### Страницы
- `/` - главная страница
- `/upload` - загрузить картинку
- `/images` - список всех картинок

### API 
```bash
# Получить список картинок (первая страница)
curl http://localhost/api/images-data/?page=1

# Загрузить картинку
curl -X POST -F "file=@photo.jpg" http://localhost/api/upload

# Удалить картинку
curl -X DELETE http://localhost/api/images/filename.jpg
```

##  Что работает

✅ **Главная страница** - просто текст и ссылки  
✅ **Загрузка** - может загружать .jpg, .png, .gif (макс 5 МБ)  
✅ **Список картинок** - показывает таблицу со всеми картинками  
✅ **Пагинация** - показывает по 10 картинок на странице  
✅ **Удаление** - кнопка удалить рядом с каждой картинкой  

##  База данных

У нас одна таблица `images`:

```
id         - порядковый номер
filename   - имя файла на сервере (генерируется сами)
original_name - имя которое загрузил пользователь
size       - размер в байтах
upload_time - когда загрузили
file_type  - jpg/png/gif
```

Пример:
```
1 | a1b2c3d4 | my_photo.jpg  | 256 | 2025-05-30 | jpg
2 | e5f6g7h8 | cat.png       | 512 | 2025-05-29 | png
```

##  Docker 

Контейнеры работают отдельно:

- **app** - Python сервер (порт 8000)
- **nginx** - раздает картинки и статику (порт 80)
- **db** - PostgreSQL база (порт 5432)

Команды:
```bash
docker compose up --build      # запустить
docker compose down            # остановить
docker compose logs -f app     # смотреть логи Python
docker compose exec app bash   # зайти внутрь контейнера
```

##  Логи

Логи пишутся в `logs/app.log`:

```
[2025-05-30 10:15:23] INFO: GET 192.168.1.1 /api/images-data/?page=1
[2025-05-30 10:15:24] INFO: Image abc12345.jpg: File upload(256000 bytes)
```

Если что-то не работает - смотри логи!

##  Какие библиотеки используем

```
pillow            - работа с картинками
psycopg           - подключение к PostgreSQL
python-dotenv     - загрузка переменных из .env
multipart         - парсинг загруженных файлов
```

##  Пагинация 

Вместо того чтобы загружать все 1000 картинок сразу, показываем по 10:

```
Пользователь кликает "Следующая"
        ↓
URL меняется на ?page=2
        ↓
JavaScript запрашивает /api/images-data/?page=2
        ↓
Backend считает: offset = (2-1)*10 = 10
        ↓
SQL: SELECT * FROM images LIMIT 10 OFFSET 10
        ↓
Получаем картинки 11-20
        ↓
Показываем их и кнопки "Предыдущая/Следующая"
```

##  Если что-то не работает

**Ошибка на порту 5432:**
```bash
docker compose logs db
# подожди 10 сек пока БД загружается
```

**Картинки не загружаются:**
```bash
ls -la images/
# проверь права доступа
```

**Nginx выдает 404:**
Проверь nginx.conf

**Все сломалось:**
```bash
docker compose down -v
docker compose up --build
```

##  Ручное тестирование

```bash
# Загрузить картинку
curl -X POST -F "file=@test.jpg" http://localhost/api/upload

# Получить список страница 1
curl http://localhost/api/images-data/?page=1

# Получить список страница 2
curl http://localhost/api/images-data/?page=2

# Удалить картинку
curl -X DELETE http://localhost/api/images/filename.jpg
```

##  Ветки в репо

| Ветка | Для чего |
|-------|----------|
| `develop` | основная разработка |
| `feature/backend` | код на Python |
| `feature/frontend` | HTML/CSS/JS |
| `feature/docker_nginx` | Docker и Nginx |
| `feature/postgres` | база данных |
| `feature/pagination` | пагинация |

##  Чего можно добавить потом

- Авторизация (логин/пароль)
- Профили пользователей
- Поиск по картинкам
- Категории
- Кэширование (Redis)
- Бэкапы базы


---

**Что-то непонятно?** Смотри логи в `logs/app.log`
