import subprocess
from pathlib import Path

from flask import Flask
from src.config import Config
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.json.ensure_ascii = False


@app.get('/health')
def health():
    return {'status': 'ok'}


app.wsgi_app = DispatcherMiddleware(Flask('root'), {'/api': app.wsgi_app})

if __name__ == '__main__':
    init_script = Path(__file__).parent / 'database' / 'initdb.sh'
    subprocess.run(
        ['sh', str(init_script)],
        check=True,
        cwd=Path(__file__).parent,
    )
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)