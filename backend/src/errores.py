def error_respuesta(mensaje, codigo):
    return {
        'errors': [
            {
                'code': codigo,
                'message': mensaje,
                'level': 'error',
                'description': mensaje,
            }
        ]
    }