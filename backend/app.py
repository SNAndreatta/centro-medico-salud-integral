import subprocess
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, redirect, request
from urllib.parse import urlencode
from src.config import Config
from src.errores import error_respuesta
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


# --- Redirección para cancelar turno desde el correo (sin login) ---
# El backend valida el token, cancela el turno y redirige al frontend,
# que es quien renderiza el HTML del modal (templates/components).
root_app = Flask('root')


def _resultado_cancelacion(titulo, mensaje, icono, exito, boton_texto, boton_url, status_code):
    """Construye los parámetros y redirige al frontend para mostrar el modal."""
    color = '#10b981' if exito else '#dc2626'   # verde éxito / rojo error
    estado = 'exito' if exito else 'error'
    params = {
        'estado': estado,
        'titulo': titulo,
        'mensaje': mensaje,
        'icono': icono,
        'color': color,
        'boton_texto': boton_texto,
        'boton_url': boton_url,
    }
    return redirect(
        f"{Config.FRONTEND_URL}/cancelar-turno?{urlencode(params)}",
        code=302,
    )


@root_app.get('/cancelar-turno/<int:id_turno>')
def cancelar_turno_desde_correo(id_turno):
    token = request.args.get('token')
    if not token:
        return _resultado_cancelacion(
            'Enlace inválido',
            'No se recibió el token de cancelación.',
            '⚠️',
            False,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
            400,
        )

    try:
        respuesta, status_code = cancelar_turno_por_token(id_turno, token)
    except ValueError as exc:
        return _resultado_cancelacion(
            'Error al cancelar',
            str(exc),
            '⚠️',
            False,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
            400,
        )

    exito = status_code == 200
    if exito:
        return _resultado_cancelacion(
            'Turno cancelado',
            'Tu turno ha sido cancelado correctamente.',
            '✅',
            True,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
            200,
        )

    # Error de negocio (token inválido, turno fuera de plazo, etc.)
    mensaje = respuesta.get('message') or respuesta.get('mensaje') or 'No se pudo cancelar el turno.'
    return _resultado_cancelacion(
        'No se pudo cancelar',
        mensaje,
        '⚠️',
        False,
        'Volver al inicio',
        Config.FRONTEND_URL or '/',
        status_code,
    )


app.wsgi_app = DispatcherMiddleware(root_app, {'/api': app.wsgi_app})

if __name__ == '__main__':
    init_script = Path(__file__).parent / 'database' / 'initdb.sh'
    subprocess.run(
        ['sh', str(init_script)],
        check=True,
        cwd=Path(__file__).parent,
    )
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
