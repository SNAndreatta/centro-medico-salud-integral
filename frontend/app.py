from flask import Flask

from src.config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.json.ensure_ascii = False

if __name__ == '__main__':
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)