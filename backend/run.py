import logging
from conversate.config import Config
from conversate.app import create_app

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = create_app(Config())

if __name__ == '__main__':
    app.run()
