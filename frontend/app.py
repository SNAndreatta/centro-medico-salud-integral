from flask import Flask, render_template, session
from routes.auth import auth_routes
from routes.recepcion import recepcion_routes
from routes.home import home_routes
from routes.medico import medico_routes
from routes.profile import profile_routes
from routes.paciente import paciente_routes
from routes.admin.abm.cobertura import cobertura_routes
from routes.admin.abm.consultorio import consultorio_routes
from routes.admin.abm.especialidad import especialidad_routes
from routes.admin.abm.medico import medico_admin_routes
from routes.admin.abm.usuario import usuario_routes
from routes.admin.dashboards.sala_espera import sala_espera_admin_routes
from routes.admin.dashboards.turnos_especialidad import turnos_especialidad_admin_routes
from routes.admin.dashboards.ausentismo import ausentismo_admin_routes
from routes.admin.dashboards.disponibilidad_consultorio import disponibilidad_consultorios_admin_routes
from routes.admin.dashboards.tiempo_espera import tiempo_espera_admin_routes

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
app.register_blueprint(cobertura_routes)
app.register_blueprint(consultorio_routes)
app.register_blueprint(especialidad_routes)
app.register_blueprint(usuario_routes)
app.register_blueprint(medico_admin_routes)
app.register_blueprint(sala_espera_admin_routes)
app.register_blueprint(turnos_especialidad_admin_routes)
app.register_blueprint(ausentismo_admin_routes)
app.register_blueprint(disponibilidad_consultorios_admin_routes)
app.register_blueprint(tiempo_espera_admin_routes)

@app.context_processor
def agregar_datos_globales():
    rol = session.get("rol", "paciente")

    return {
        "rol": rol
    }

if __name__ == "__main__":
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )