import logging
import uuid
from app.settings import MEDIA_PATH
from base_handler import BaseHandler


logger = logging.getLogger(__name__)

# в этом хэндлере должна быть описана бизнес логика
class ImageHostingHandler(BaseHandler):

   # функция принимает GET-запрос и выдает соответствующую страницу
    def do_GET(self):
        logger.info(f"GET {self.client_address[0]} {self.path}")

        if self.path.startswith("/api/"):
            if self.path == "/api/images":
                self.get_images()
            elif self.path.startswith("/api/images/"):
                name = self.path.split("/")[-1]
                self.send_media_file(name)
            else:
                self.html_response("API Not Found", 404)

        elif self.path == "/":
            self.template_response('index.html')
        elif self.path == "/upload":
            self.template_response('upload.html')
        elif self.path == "/images":
            self.template_response('images.html')
        elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
            self.send_static_file(self.path)
        else :
            self.html_response(f"GET route not found: {self.path}", 404)

    def do_POST(self):
        logger.info(f"POST {self.client_address[0]} {self.path}")
        if self.path == "/api/upload":
            unique_id = uuid.uuid4()
            self.upload_file(str(unique_id)[:8])
        else:
            self.html_response(f"POST route not found: {self.path}", 404)

    def do_DELETE(self):
        if self.path.startswith("/api/images/"):
            name = self.path.split("/")[-1]
            self.delete_image(name)


    def get_images(self):
        self.json_response({
            "images":[f.name for f in MEDIA_PATH.iterdir() if
                      f.name != ".gitkeep"]
        })


    def delete_image(self, name):
        try:
            (MEDIA_PATH / name).unlink()
            logger.info(f"image {name} deleted successfully")
            self.json_response({"message": "Image deleted succesfully"}, status_code = 204)
        except FileNotFoundError:
            logger.info(f"image {name} not found (on delete)")
            self.json_response({"message": "Image not found"}, status_code = 404)
