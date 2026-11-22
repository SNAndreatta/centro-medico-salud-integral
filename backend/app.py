import subprocess
from pathlib import Path

from flask import Flask, request
from src.config import Config
from src.routes.auth_routes import auth_bp
from src.routes.usuarios_routes import usuarios_bp
from src.routes.medicos_routes import medicos_bp
from src.routes.pacientes_routes import pacientes_bp
from src.routes.agendas_routes import agendas_bp
from src.routes.turnos_routes import turnos_bp
from src.routes.estadisticas_routes import estadisticas_bp
from src.routes.especialidades_routes import especialidades_bp
from src.routes.coberturas_routes import coberturas_bp
from src.routes.consultorios_routes import consultorios_bp
from src.services.turnos_services import ejecutar_ausentismo_automatico
from src.repositories.turnos_repositories import intentar_adquirir_ejecucion_tarea
from src.utils.fechas import ahora_local
from src.utils.http_errors import handle_unexpected_errors
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.json.ensure_ascii = False
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(medicos_bp)
app.register_blueprint(consultorios_bp)
app.register_blueprint(pacientes_bp)
app.register_blueprint(agendas_bp)
app.register_blueprint(turnos_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(especialidades_bp)
app.register_blueprint(coberturas_bp)

@app.before_request
def verificar_ausentismo_lazy():
    try:
        debe_ejecutar = intentar_adquirir_ejecucion_tarea(
            'ausentismo_automatico',
            ahora_local(),
            Config.INTERVALO_AUSENTISMO_SEGUNDOS,
        )
        if debe_ejecutar:
            ejecutar_ausentismo_automatico()
    except Exception:
        app.logger.exception('No se pudo ejecutar el procesamiento automático de ausentismo')


@app.get('/health')
@handle_unexpected_errors
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