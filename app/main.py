

from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

from dotenv import load_dotenv

from app.image_hosting_handler import ImageHostingHandler
from app.settings import LOG_PATH

load_dotenv()

#loglevel = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers = [
                        logging.StreamHandler()
                        logging.FileHandler(LOG_PATH/ "server.log")
                    ]
                    )

logger = logging.getLogger(__name__)


def run(server_address = ('', 8000),server_class=HTTPServer, handler_class=ImageHostingHandler):

    logger.info(f'Starting server on {server_address}')
    httpd = server_class(server_address, handler_class)
    try:

        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        httpd.server_close()
    except Exception as e:
        logger.error(f'Exception occurred: {e}')


if __name__ == '__main__':
    run()