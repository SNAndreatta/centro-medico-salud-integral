import requests
from flask import current_app, session


class ErrorAPI(Exception):
    def __init__(self, mensaje, status=500):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def mensaje_error(datos):
    """Extrae el mensaje del formato de errores del backend."""
    if not isinstance(datos, dict):
        return None

    mensaje = datos.get("mensaje") or datos.get("error") or datos.get("detalle")
    errores = datos.get("errors")
    if not mensaje and isinstance(errores, list) and errores:
        primero = errores[0]
        if isinstance(primero, dict):
            mensaje = primero.get("message") or primero.get("description")

    return mensaje


def api(metodo, ruta, codigo_esperado=None, **kwargs):
    headers = {}
    token = session.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = requests.request(
            metodo,
            f"{current_app.config['BACKEND_URL']}{ruta}",
            headers=headers,
            timeout=10,
            **kwargs,
        )
    except requests.RequestException:
        raise ErrorAPI("No se pudo conectar con el servidor.", 503)

    try:
        datos = r.json()
    except ValueError:
        datos = {}

    if not r.ok or (codigo_esperado is not None and r.status_code != codigo_esperado):
        print("API ERROR:", metodo, ruta, r.status_code, r.text[:300], flush=True)
        raise ErrorAPI(
            mensaje_error(datos) or "Ocurrió un error inesperado.",
            r.status_code,
        )

    return datos
