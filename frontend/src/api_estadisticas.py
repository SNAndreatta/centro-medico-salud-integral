from .api import api


def ausentismo(parametros=None):
    return api('GET', '/estadisticas/ausentismo', params=parametros or {})


def tiempo_espera(parametros=None):
    return api('GET', '/estadisticas/tiempo_espera', params=parametros or {})


def turnos_por_especialidad(parametros=None):
    return api('GET', '/estadisticas/turnos-especialidad', params=parametros or {})
