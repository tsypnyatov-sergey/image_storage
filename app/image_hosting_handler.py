from base_handler import BaseHandler

# в этом хэндлере должна быть описана бизнес логика
class ImageHostingHandler(BaseHandler):

   # функция принимает GET-запрос и выдает соответствующую страницу
    def do_GET(self):
        if self.path == "/":
            self.template_response("index.html")
        elif self.path == "/upload":
            self.html_response("Upload page")
        elif self.path == "/images":
            self.html_response("images page")
        else :
            self.html_response("Not Found", 404)

