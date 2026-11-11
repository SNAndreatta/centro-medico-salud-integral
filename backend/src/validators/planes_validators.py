from src.validators.common import validar_cuerpo_con_nombre


def validar_datos_plan(datos):
    return validar_cuerpo_con_nombre(
        datos,
        'El cuerpo debe incluir únicamente el campo nombre',
    )
