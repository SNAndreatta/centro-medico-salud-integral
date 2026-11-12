import requests
from flask import current_app, session


class ErrorAPI(Exception):
    def __init__(self, mensaje, status=500):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.status = status


def api(metodo, ruta, **kwargs):
    headers = kwargs.pop("headers", {})
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

    if not r.ok:
        print("API ERROR:", metodo, ruta, r.status_code, r.text[:300], flush=True)
        mensaje = None
        if isinstance(datos, dict):
            mensaje = datos.get("mensaje") or datos.get("error")
        raise ErrorAPI(mensaje or "Ocurrió un error inesperado.", r.status_code)

    return datos