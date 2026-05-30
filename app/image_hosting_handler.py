import logging

from psycopg import DatabaseError

from app.base_handler import BaseHandler
from app.db_manager import DBManager
from app.settings import MEDIA_PATH

logger = logging.getLogger(__name__)


# в этом хэндлере должна быть описана бизнес логика
class ImageHostingHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        self.db: DBManager = DBManager()
        super().__init__(*args, **kwargs)

    # функция принимает GET-запрос и выдает соответствующую страницу
    def do_GET(self):

        logger.info(f"GET {self.client_address[0]} {self.path}")

        api_handlers = {
            "/api/images": self.get_images_names,
            "/api/images-data/": self.get_images,
        }

        templates = {
            "/": 'index.html',
            "/upload": 'upload.html',
            "/images": 'images.html',
        }

        if self.path in templates:
            self.template_response(templates[self.path])
        elif self.path in api_handlers:
            api_handlers[self.path]()
        else:
            self.html_response(f"GET route not found: {self.path}", 404)

    def do_POST(self):
        logger.info(f"POST {self.client_address[0]}: {self.path}")

        if self.path == "/api/upload":
            image_dict = self.upload_file()
            if image_dict:
                self.db.add_image(image_dict)
                self.json_response({
                    "message": "Upload Successful",
                    "image": image_dict,
                }, 201)
                return
            else:
                self.json_response({
                    "message": "Invalid upload file",
                }, 400)
                return
        else:
            self.html_response(f"POST route not found: {self.path}", 404)
            return

    def do_DELETE(self):
        logger.info(f"DELETE {self.client_address[0]}: {self.path}")

        if self.path.startswith('/api/images/'):
            name = self.path.split('/')[-1]
            name, file_type = name.rsplit('.', 1)
            self.delete_image(name, file_type)

    def get_images_names(self):

        self.json_response({
            "images": self.db.get_images_names()
        })

    def get_images(self):
        images = self.db.get_images()

        res_images = []

        for i in images:
            upload_time = i[4]

            if upload_time:
                if hasattr(upload_time, 'strftime'):
                    upload_time = upload_time.strftime('%Y-%m-%d %H:%M')
                else:
                    upload_time = str(upload_time)
            else:
                upload_time = None

            res_images.append({
                    'id': i[0],
                    'filename': i[1],
                    'original_name': i[2],
                    'size': i[3],
                    'upload_time': upload_time,
                    'file_type': i[5]
                })
        self.json_response({
            'images': res_images
        })

    def delete_image(self, name: str, file_type: str):
        try:
            self.db.delete_image(name)
            (MEDIA_PATH / (name + '.' + file_type)).unlink()
            logger.info(f"Image {name} deleted successfully")
            self.json_response({'message': 'Image deleted successfully'},
                               status_code=204)
        except FileNotFoundError:
            logger.info(f"File {name} not found (on delete)")
            self.json_response({'message': 'Image not found'}, 404)
        except DatabaseError:
            logger.info(f"{name} not found in database (on delete)")
            self.json_response({'message': 'Image not found'}, 404)
