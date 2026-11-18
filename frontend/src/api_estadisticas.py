"""Wrappers de los endpoints de estadísticas."""

from src.api import api


def sala_espera(parametros=None):
    return api("GET", "/estadisticas/sala_espera", params=parametros or {})


def ocupacion_consultorios(parametros=None):
    return api(
        "GET", "/estadisticas/ocupacion_consultorios",
        params=parametros or {},
    )


def ausentismo(parametros=None):
    return api("GET", "/estadisticas/ausentismo", params=parametros or {})


def tiempo_espera(parametros=None):
    return api("GET", "/estadisticas/tiempo_espera", params=parametros or {})


def turnos_por_especialidad(parametros=None):
    return api("GET", "/estadisticas/turnos-especialidad", params=parametros or {})
