"""Acceso a turnos, agendas y acciones sobre turnos."""

from src.api import api
from src.normalizar import como_lista, normalizar_turno
from src.tiempo import hoy_local


def listar(parametros=None):
    """Turnos disponibles según el filtro que permite el token."""
    return como_lista(api("GET", "/turnos", params=parametros or {}), "turnos")


def disponibles(**filtros):
    parametros = {clave: valor for clave, valor in filtros.items()
                  if valor not in (None, "")}
    datos = como_lista(
        api("GET", "/turnos/disponibles", params=parametros), "turnos"
    )
    return [normalizar_turno(turno) for turno in datos]


def mis_turnos_paciente():
    # GET /turnos ya limita el resultado al paciente autenticado (JWT).
    return [normalizar_turno(turno) for turno in listar()]


def proximos_turnos_paciente(limite=3):
    """Turnos futuros (reservados o confirmados) del paciente."""
    activos = [
        turno for turno in mis_turnos_paciente()
        if turno["estado"] in ("reservado", "confirmado") and turno["es_futuro"]
    ]
    activos.sort(key=lambda turno: (turno["fecha_iso"], turno["hora"]))
    return activos[:limite]


def turnos_del_dia_medico():
    """Turnos de hoy del médico autenticado."""
    hoy = hoy_local().isoformat()
    turnos = listar({"fecha_desde": hoy, "fecha_hasta": hoy})

    return [normalizar_turno(turno, vista="medico_home") for turno in turnos]


def generar_turnos():
    return api("POST", "/turnos/generar")


def cancelar_turno(id_turno):
    api("POST", "/turnos/cancelar", json={"id_turno": id_turno})


def reservar_turno(id_turno, datos):
    return api("POST", f"/turnos/{id_turno}/reservar", json=datos)


def marcar_atendido(id_turno):
    api("PUT", f"/turnos/{id_turno}/estado", json={"estado": "atendido"})


def checkin(token):
    api("POST", "/turnos/checkin", json={"token": token})


def obtener_agendas(id_medico=None):
    parametros = {"id_medico": id_medico} if id_medico else {}
    return como_lista(api("GET", "/agendas", params=parametros), "agendas")


def crear_agenda(datos):
    api("POST", "/agendas", json=datos)
