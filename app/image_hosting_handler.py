from base_handler import BaseHandler

# в этом хэндлере должна быть описана бизнес логика
class ImageHostingHandler(BaseHandler):

   # функция принимает GET-запрос и выдает соответствующую страницу
    def do_GET(self):
        if self.path == "/":
            self.template_response('index.html')
        elif self.path == "/upload":
            self.template_response('upload.html')
        elif self.path == "/images":
            self.template_response('images.html')
        elif any((self.path.endswith(ext) for ext in ['.css', '.js', '.png'])):
            self.send_file(self.path)
        else :
            self.html_response("Not Found", 404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data_input = self.rfile.read(content_length)
        with open("recived.jpg", "wb") as f:
            f.write(data_input)
        self.response("Got your file!", 'text/plain')

