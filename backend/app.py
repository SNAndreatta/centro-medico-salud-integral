import subprocess
from pathlib import Path

from flask import Flask, request
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


# --- Página HTML para cancelar turno desde el correo (sin login) ---
root_app = Flask('root')


def _pagina_cancelacion(titulo, mensaje, icono, exito, boton_texto, boton_url):
    """Devuelve un string HTML sencillo y bonito para mostrar tras cancelar un turno."""
    color = '#10b981' if exito else '#dc2626'
    frente_color = '#ffffff' if exito else '#ffffff'
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{titulo} - Centro Médico Salud Integral</title>
      <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; background: #f5f8fb; color: #1f2937;
                display: flex; align-items: center; justify-content: center;
                min-height: 100vh; padding: 24px; }}
        .card {{ background: white; border-radius: 12px; padding: 40px 32px;
                 max-width: 420px; width: 100%; text-align: center;
                 box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        .icon {{ font-size: 56px; color: {color}; margin-bottom: 16px; display: block; }}
        h1 {{ color: #0f172a; margin-bottom: 12px; font-size: 24px; }}
        p {{ color: #4b5563; margin-bottom: 24px; font-size: 16px; line-height: 1.5; }}
        .btn {{ display: inline-flex; align-items: center; justify-content: center;
                background: {color}; color: {frente_color}; text-decoration: none;
                padding: 14px 28px; border-radius: 8px; font-weight: 700; font-size: 16px;
                margin-bottom: 12px; }}
        .btn:hover {{ filter: brightness(0.95); }}
        .btn-sec {{ display: inline-block; background: #e5e7eb; color: #374151;
                    text-decoration: none; padding: 10px 20px; border-radius: 8px;
                    font-size: 14px; }}
        .btn-sec:hover {{ background: #d1d5db; }}
        .popup {{ position: fixed; inset: 0; background: rgba(0,0,0,0.55);
                  display: flex; align-items: center; justify-content: center;
                  z-index: 1000; }}
        .popup-content {{ background: white; padding: 32px; border-radius: 12px;
                          max-width: 360px; width: 90%; text-align: center;
                          box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                          animation: fadeIn 0.3s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(-10px); }}
                             to {{ opacity: 1; transform: translateY(0); }} }}
        .popup .icon {{ font-size: 64px; margin-bottom: 16px; }}
        .popup h2 {{ margin-bottom: 12px; font-size: 22px; color: #0f172a; }}
        .popup p {{ color: #4b5563; margin-bottom: 24px; font-size: 16px; }}
        .popup .btn-ok {{ background: {color}; color: {frente_color}; border: none;
                          padding: 12px 28px; border-radius: 8px; font-weight: 700;
                          font-size: 16px; cursor: pointer; width: 100%; }}
        .popup .btn-ok:hover {{ filter: brightness(0.9); }}
      </style>
    </head>
    <body>
      <div class="popup" id="popup">
        <div class="popup-content">
          <span class="icon">{icono}</span>
          <h2>{titulo}</h2>
          <p>{mensaje}</p>
          <button class="btn-ok" id="cerrarPopup">Aceptar</button>
        </div>
      </div>

      <div class="card">
        <span class="icon">{icono}</span>
        <h1>{titulo}</h1>
        <p>{mensaje}</p>
        <a href="{boton_url}" class="btn">{boton_texto}</a>
      </div>

      <script>
        document.getElementById('cerrarPopup').addEventListener('click', function() {{
          document.getElementById('popup').style.display = 'none';
        }});
        document.getElementById('popup').addEventListener('click', function(e) {{
          if (e.target === this) this.style.display = 'none';
        }});
      </script>
    </body>
    </html>
    """


@root_app.get('/cancelar-turno/<int:id_turno>')
def cancelar_turno_desde_correo(id_turno):
    token = request.args.get('token')
    if not token:
        html = _pagina_cancelacion(
            'Enlace inválido',
            'No se recibió el token de cancelación.',
            '⚠️',
            False,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
        )
        return html, 400, {'Content-Type': 'text/html; charset=utf-8'}

    try:
        respuesta, status_code = cancelar_turno_por_token(id_turno, token)
    except ValueError as exc:
        html = _pagina_cancelacion(
            'Error al cancelar',
            str(exc),
            '⚠️',
            False,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
        )
        return html, 400, {'Content-Type': 'text/html; charset=utf-8'}

    exito = status_code == 200
    if exito:
        html = _pagina_cancelacion(
            'Turno cancelado',
            'Tu turno ha sido cancelado correctamente.',
            '✅',
            True,
            'Volver al inicio',
            Config.FRONTEND_URL or '/',
        )
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}

    # Error de negocio (token inválido, turno fuera de plazo, etc.)
    mensaje = respuesta.get('message') or respuesta.get('mensaje') or 'No se pudo cancelar el turno.'
    html = _pagina_cancelacion(
        'No se pudo cancelar',
        mensaje,
        '⚠️',
        False,
        'Volver al inicio',
        Config.FRONTEND_URL or '/',
    )
    return html, status_code, {'Content-Type': 'text/html; charset=utf-8'}


app.wsgi_app = DispatcherMiddleware(root_app, {'/api': app.wsgi_app})

if __name__ == '__main__':
    init_script = Path(__file__).parent / 'database' / 'initdb.sh'
    subprocess.run(
        ['sh', str(init_script)],
        check=True,
        cwd=Path(__file__).parent,
    )
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)