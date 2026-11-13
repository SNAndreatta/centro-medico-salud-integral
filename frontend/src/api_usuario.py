from flask import session

from src.api import api
from src.api_paciente import _buscar, _fecha, _iniciales


def perfil_usuario():
    """Perfil de la cuenta autenticada (admin, recepción o médico).

    `GET /usuarios/me` devuelve los datos comunes de `usuario` y, para los
    médicos, su perfil anidado en `medico` (matrícula y especialidad).
    """
    p = api("GET", "/usuarios/me")

    nombre = _buscar(p, "nombre", default=session.get("nombre", ""))
    apellido = _buscar(p, "apellido", default=session.get("apellido", ""))
    fecha_nac = _buscar(p, "fecha_nacimiento")
    fecha_reg = _buscar(p, "fecha_creacion", "fecha_registro")

    return {
        "nombre": nombre,
        "apellido": apellido,
        "iniciales": _iniciales(f"{nombre} {apellido}"),
        "email": _buscar(p, "correo_electronico", "email", default=""),
        "documento": _buscar(p, "dni", "documento", default=""),
        "fecha_nacimiento": (
            _fecha(fecha_nac).strftime("%d/%m/%Y") if fecha_nac else "No informada"
        ),
        "fecha_registro": _fecha(fecha_reg).strftime("%d/%m/%Y") if fecha_reg else "-",
        "matricula": _buscar(p, "matricula", default="-") or "-",
    }
