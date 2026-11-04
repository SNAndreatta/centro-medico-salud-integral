import re
from datetime import date, time

from src.errores import error_respuesta
from src.utils.utils import validar_id_positivo

def _booleano_opcional(valor, nombre):
    if valor is None:
        return None, None
    normalizado = str(valor).strip().lower()
    if normalizado == 'true':
        return True, None
    if normalizado == 'false':
        return False, None
    return None, error_respuesta(f'{nombre} debe ser true o false', 'FILTRO_INVALIDO')


def validar_filtros_agendas(parametros):
    filtros = {}
    for nombre in ('id_medico', 'id_consultorio'):
        valor, error = validar_id_positivo(parametros.get(nombre), nombre)
        if error:
            return None, error
        filtros[nombre] = valor

    vigente, error = _booleano_opcional(parametros.get('vigente'), 'vigente')
    if error:
        return None, error
    filtros['vigente'] = vigente
    return filtros, None

def _fecha_obligatoria(valor, nombre):
    if not isinstance(valor, str):
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    try:
        fecha = date.fromisoformat(valor)
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')

    if fecha.isoformat() != valor:
        return None, error_respuesta(f'{nombre} debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')
    return fecha, None


def _hora_obligatoria(valor, nombre):
    if not isinstance(valor, str):
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')

    hora_texto = valor.strip()
    if not re.fullmatch(r'\d{2}:\d{2}(:\d{2})?$', hora_texto):
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')

    try:
        hora = time.fromisoformat(hora_texto)
    except ValueError:
        return None, error_respuesta(f'{nombre} debe tener formato HH:MM o HH:MM:SS', 'HORA_INVALIDA')

    if hora.tzinfo is not None:
        return None, error_respuesta(f'{nombre} no debe incluir zona horaria', 'HORA_INVALIDA')

    return hora.strftime('%H:%M:%S'), None


def validar_datos_agenda(datos):
    campos_esperados = (
        'id_medico',
        'id_consultorio',
        'duracion_turno',
        'fecha_inicio',
        'fecha_hasta',
        'dias',
    )

    if set(datos.keys()) != set(campos_esperados):
        return None, error_respuesta('El cuerpo debe incluir id_medico, id_consultorio, duracion_turno, fecha_inicio, fecha_hasta y dias', 'CUERPO_INVALIDO')

    for nombre in ('id_medico', 'id_consultorio'):
        valor = datos[nombre]

        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            return None, error_respuesta(f'{nombre} debe ser un entero positivo', 'DATOS_INVALIDOS')

    duracion = datos['duracion_turno']

    if isinstance(duracion, bool) or not isinstance(duracion, int) or duracion <= 0:
        return None, error_respuesta('duracion_turno debe ser un entero positivo en minutos', 'DATOS_INVALIDOS')

    fecha_inicio, error = _fecha_obligatoria(datos['fecha_inicio'], 'fecha_inicio')
    if error:
        return None, error

    fecha_hasta, error = _fecha_obligatoria(datos['fecha_hasta'], 'fecha_hasta')
    if error:
        return None, error

    if fecha_inicio > fecha_hasta:
        return None, error_respuesta('fecha_inicio no puede ser posterior a fecha_hasta', 'RANGO_FECHAS_INVALIDO')

    dias = datos['dias']

    if not isinstance(dias, list) or not dias:
        return None, error_respuesta('Debe especificarse al menos una jornada semanal', 'DIAS_INVALIDOS')

    dias_validados = []
    franjas_por_dia = {}

    for dia in dias:
        if not isinstance(dia, dict):
            return None, error_respuesta('Cada elemento de dias debe ser un objeto', 'DIAS_INVALIDOS')

        if set(dia) != {'dia_semana', 'hora_inicio', 'hora_fin'}:
            return None, error_respuesta('Cada jornada debe incluir dia_semana, hora_inicio y hora_fin', 'DIAS_INVALIDOS')

        dia_semana = dia['dia_semana']

        if(isinstance(dia_semana, bool) or not isinstance(dia_semana, int) or dia_semana < 1 or dia_semana > 7):
            return None, error_respuesta('dia_semana debe ser un entero entre 1 y 7', 'DIA_SEMANA_INVALIDO')

        hora_inicio, error = _hora_obligatoria(dia['hora_inicio'], 'hora_inicio')
        if error:
            return None, error

        hora_fin, error = _hora_obligatoria(dia['hora_fin'], 'hora_fin')
        if error:
            return None, error

        inicio = time.fromisoformat(hora_inicio)
        fin = time.fromisoformat(hora_fin)

        if inicio >= fin:
            return None, error_respuesta('hora_inicio debe ser anterior a hora_fin', 'RANGO_HORARIO_INVALIDO')

        segundos_inicio = (inicio.hour * 3600 + inicio.minute * 60 + inicio.second)
        segundos_fin = (fin.hour * 3600 + fin.minute * 60 + fin.second)

        duracion_segundos = duracion * 60

        if(segundos_fin - segundos_inicio) % duracion_segundos != 0:
            return None, error_respuesta('La duracion de la jornada debe ser multiplo de duracion_turno', 'DURACION_JORNADA_INVALIDA')

        franjas = franjas_por_dia.setdefault(dia_semana, [])

        for inicio_existente, fin_existente in franjas:
            if inicio < fin_existente and fin > inicio_existente:
                return None, error_respuesta('Har jornadas superpuestas para el mismo dia de la semana', 'JORNADAS_SUPERPUESTAS')

        franjas.append((inicio, fin))
        dias_validados.append({
            'dia_semana': dia_semana,
            'horario_inicio_jornada': hora_inicio,
            'horario_final_jornada': hora_fin,
        })

    return {
        'id_medico': datos['id_medico'],
        'id_consultorio': datos['id_consultorio'],
        'duracion_turno': duracion,
        'fecha_inicio': fecha_inicio.isoformat(),
        'fecha_hasta': fecha_hasta.isoformat(),
        'dias': dias_validados,
    }, None

def validar_datos_actualizacion_agenda(datos):
    campos_esperados = {'fecha_hasta'}

    if set(datos.keys()) !=  campos_esperados:
        return None, error_respuesta('El cuerpo debe contener unicamente el campo fecha_hasta', 'CUERPO_INVALIDO')

    fecha_hasta = datos['fecha_hasta']

    if not isinstance(fecha_hasta, str):
        return None, error_respuesta('La fecha_hasta debe ser un texto con formato YYYY-MM-DD', 'FECHA_INVALIDA')

    try:
        fecha_validada = date.fromisoformat(fecha_hasta)
    except ValueError:
        return None, error_respuesta('La fecha_hasta no tiene un formato valido', 'FECHA_INVALIDA')

    if fecha_validada.isoformat() != fecha_hasta:
        return None, error_respuesta('La fecha_hasta debe tener formato YYYY-MM-DD', 'FECHA_INVALIDA')

    return {'fecha_hasta': fecha_hasta}, None
