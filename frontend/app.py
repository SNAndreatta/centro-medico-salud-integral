from flask import Flask, render_template
from routes.auth import auth_routes
from routes.recepcion import recepcion_routes
from routes.home import home_routes
from routes.medico import medico_routes
from routes.profile import profile_routes
from routes.paciente import paciente_routes
from routes.admin import admin_routes

from src.config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.json.ensure_ascii = False

app.register_blueprint(auth_routes)
app.register_blueprint(recepcion_routes)
app.register_blueprint(home_routes)
app.register_blueprint(medico_routes)
app.register_blueprint(profile_routes)
app.register_blueprint(paciente_routes)
app.register_blueprint(admin_routes)

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )