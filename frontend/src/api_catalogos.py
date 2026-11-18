"""Acceso a catálogos y entidades que no son turnos ni usuarios."""

from src.api import api
from src.normalizar import (
    color_avatar,
    como_lista,
    formatear_fecha,
    g,
    iniciales,
    nombre_completo,
)

SIN_ENVIAR = object()


def _entero(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return valor


def obtener_especialidades():
    datos = como_lista(api("GET", "/especialidades"), "especialidades")

    return [
        {
            "id": _entero(g(especialidad, "id_especialidad", "id")),
            "nombre": g(especialidad, "nombre_especialidad", "nombre"),
            "cantidad_medicos": int(g(especialidad, "cantidad_medicos") or 0),
        }
        for especialidad in datos
    ]


def obtener_coberturas():
    datos = como_lista(api("GET", "/coberturas"), "coberturas")

    return [
        {
            "id": _entero(g(cobertura, "id_cobertura", "id")),
            "nombre": g(cobertura, "nombre"),
            "cantidad_medicos": int(g(cobertura, "cantidad_medicos") or 0),
        }
        for cobertura in datos
    ]


def listar_medicos(parametros=None):
    datos = como_lista(api("GET", "/medicos", params=parametros or {}), "medicos")

    return [
        {
            "id": _entero(g(medico, "id_medico", "id")),
            "id_usuario": _entero(g(medico, "id_usuario")),
            "nombre": g(medico, "nombre") or '',
            "apellido": g(medico, "apellido") or '',
            "nombre_completo": nombre_completo(
                g(medico, "nombre"), g(medico, "apellido")
            ),
            "iniciales": iniciales(g(medico, "nombre"), g(medico, "apellido")),
            "matricula": g(medico, "matricula"),
            "id_especialidad": _entero(g(medico, "id_especialidad")),
            "especialidad": g(medico, "nombre_especialidad", "especialidad"),
        }
        for medico in datos
    ]


def medicos_por_especialidad(id_especialidad, id_cobertura=SIN_ENVIAR):
    medicos = listar_medicos({"id_especialidad": id_especialidad})

    aceptan = None
    if id_cobertura is not SIN_ENVIAR and id_cobertura:
        aceptan = {
            medico["id"] for medico in listar_medicos({
                "id_especialidad": id_especialidad,
                "id_cobertura": id_cobertura,
            })
        }

    es_particular = id_cobertura is not SIN_ENVIAR and not id_cobertura

    return [
        {
            "id": medico["id"],
            "nombre": medico["nombre_completo"],
            "iniciales": medico["iniciales"],
            "matricula": medico["matricula"],
            "especialidad": medico["especialidad"],
            "acepta_cobertura": (
                None if es_particular or aceptan is None
                else medico["id"] in aceptan
            ),
            "es_particular": es_particular,
        }
        for medico in medicos
    ]


def obtener_medico(id_medico):
    return (api("GET", f"/medicos/{id_medico}") or {}).get("medico")


def coberturas_medico(id_medico):
    """Coberturas ya asociadas a un médico."""
    if not id_medico:
        return []

    datos = api("GET", f"/medicos/{id_medico}/coberturas") or {}

    return [
        {
            "id": _entero(g(cobertura, "id_cobertura", "id")),
            "nombre": g(cobertura, "nombre"),
        }
        for cobertura in como_lista(datos, "coberturas")
    ]


def agregar_coberturas_medico(id_medico, ids_cobertura):
    """Asocia al médico las coberturas nuevas elegidas en el formulario."""
    for id_cobertura in ids_cobertura:
        api(
            "POST",
            f"/medicos/{id_medico}/coberturas",
            json={"id_cobertura": int(id_cobertura)},
        )


def quitar_cobertura_medico(id_medico, id_cobertura):
    api("DELETE", f"/medicos/{id_medico}/coberturas/{id_cobertura}")


def obtener_consultorios():
    datos = como_lista(api("GET", "/consultorios"), "consultorios")

    return [
        {
            "id": _entero(g(consultorio, "id_consultorio", "id")),
            "piso": _entero(g(consultorio, "piso")),
            "numero": _entero(g(consultorio, "numero", "numero_consultorio")),
        }
        for consultorio in datos
    ]


def crear_cobertura(nombre):
    api("POST", "/coberturas", json={"nombre": nombre})


def editar_cobertura(id_cobertura, nombre):
    api("PUT", f"/coberturas/{id_cobertura}", json={"nombre": nombre})


def eliminar_cobertura(id_cobertura):
    api("DELETE", f"/coberturas/{id_cobertura}")


def crear_consultorio(numero, piso):
    api("POST", "/consultorios", json={"numero": numero, "piso": piso})


def editar_consultorio(id_consultorio, numero, piso):
    api("PUT", f"/consultorios/{id_consultorio}",
        json={"numero": numero, "piso": piso})


def eliminar_consultorio(id_consultorio):
    api("DELETE", f"/consultorios/{id_consultorio}")


def crear_especialidad(nombre):
    api("POST", "/especialidades", json={"nombre": nombre})


def editar_especialidad(id_especialidad, nombre):
    api("PUT", f"/especialidades/{id_especialidad}", json={"nombre": nombre})


def eliminar_especialidad(id_especialidad):
    api("DELETE", f"/especialidades/{id_especialidad}")


def normalizar_paciente(paciente, indice=0):
    nombre = g(paciente, "nombre")
    apellido = g(paciente, "apellido")
    nacimiento = g(paciente, "fecha_nacimiento")
    registro = g(paciente, "fecha_creacion", "fecha_registro")

    return {
        "id": g(paciente, "id_paciente", "id"),
        "nombre": nombre or '',
        "apellido": apellido or '',
        "nombre_completo": nombre_completo(nombre, apellido),
        "iniciales": iniciales(nombre, apellido),
        "cobertura": g(paciente, "cobertura", "nombre_cobertura") or 'Particular',
        "email": g(paciente, "correo_electronico", "email") or '-',
        "documento": g(paciente, "dni", "documento") or '-',
        "fecha_nacimiento": (
            formatear_fecha(nacimiento) if nacimiento else '-'
        ),
        "fecha_registro": formatear_fecha(registro) if registro else '-',
        "nro_afiliado": g(paciente, "nro_afiliado") or '-',
        "color_fondo": color_avatar(indice),
    }


def obtener_pacientes():
    datos = api("GET", "/pacientes") or {}

    return [
        normalizar_paciente(paciente, indice)
        for indice, paciente in enumerate(como_lista(datos, "pacientes"))
    ]


def obtener_paciente(id_paciente):
    datos = api("GET", f"/pacientes/{id_paciente}") or {}
    paciente = datos.get("paciente")

    if not paciente:
        return None

    return normalizar_paciente(paciente)
