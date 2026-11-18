"""Acceso público (sin token) para login y registro."""

from src.api import ErrorAPI, api
from src.api_catalogos import obtener_coberturas

MENSAJE_LOGIN = "Correo electrónico o contraseña incorrectos."
MENSAJE_REGISTRO = (
    "No se pudo crear la cuenta. Revisá los datos e intentá nuevamente."
)


def coberturas():
    """Coberturas válidas para el selector del registro."""
    return [
        cobertura for cobertura in obtener_coberturas()
        if cobertura["id"] and cobertura["nombre"]
    ]


def login(correo_electronico, password):
    try:
        return api(
            "POST",
            "/auth/login",
            json={
                "correo_electronico": correo_electronico,
                "password": password,
            },
        )
    except ErrorAPI as error:
        raise ErrorAPI(error.mensaje or MENSAJE_LOGIN, error.status) from error


def registrar(datos):
    try:
        return api("POST", "/pacientes", json=datos, codigo_esperado=201)
    except ErrorAPI as error:
        raise ErrorAPI(error.mensaje or MENSAJE_REGISTRO, error.status) from error
