from src.errores import error_respuesta

CAMPOS_PERMITIDOS = {'numero', 'piso'}

def validar_datos_consultorio(datos):
    if(not isinstance(datos, dict) or 'numero' not in datos or not set(datos).issubset(CAMPOS_PERMITIDOS)):
        return None, error_respuesta('El cuerpo debe incluir el campo numero y opcionalmete piso', 'CUERPO_INVALIDO')

    numero = datos['numero']
    if isinstance(numero, bool) or not isinstance(numero, int) or numero <= 0:
        return None, error_respuesta('El numero del consultorio debe ser un entero positivo', 'DATOS_INVALIDOS')

    piso = datos.get('piso')
    if piso is not None and(isinstance(piso, bool) or not isinstance(piso, int)):
        return None, error_respuesta('El piso debe ser un numero entero o null', 'DATOS_INVALIDOS')

    return {
        'numero': numero,
        'piso': piso,
    }, None