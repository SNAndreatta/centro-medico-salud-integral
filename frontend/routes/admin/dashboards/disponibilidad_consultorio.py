from flask import Blueprint, render_template, request
from datetime import date

disponibilidad_consultorios_admin_routes = Blueprint('disponibilidad_admin_routes', __name__)

@disponibilidad_consultorios_admin_routes.route("/admin/disponibilidad-consultorios")
def disponibilidad_consultorios():

    fecha = request.args.get("fecha", date.today().isoformat())

    pisos = [
        {
            "numero": 1,
            "consultorios": [
                {
                    "id": 1,
                    "numero": 111,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": False},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 2,
                    "numero": 112,
                    "horarios": [
                        {"hora": "08:00", "disponible": False},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": False}
                    ]
                },
                {
                    "id": 3,
                    "numero": 113,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": False},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 4,
                    "numero": 114,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": False},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                }
            ]
        },
        {
            "numero": 2,
            "consultorios": [
                {
                    "id": 5,
                    "numero": 201,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": False},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 6,
                    "numero": 202,
                    "horarios": [
                        {"hora": "08:00", "disponible": False},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 7,
                    "numero": 203,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": False},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 8,
                    "numero": 204,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": False}
                    ]
                }
            ]
        },
        {
            "numero": 3,
            "consultorios": [
                {
                    "id": 9,
                    "numero": 301,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": False},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 10,
                    "numero": 302,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": False},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 11,
                    "numero": 303,
                    "horarios": [
                        {"hora": "08:00", "disponible": False},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": True}
                    ]
                },
                {
                    "id": 12,
                    "numero": 304,
                    "horarios": [
                        {"hora": "08:00", "disponible": True},
                        {"hora": "09:00", "disponible": True},
                        {"hora": "10:00", "disponible": True},
                        {"hora": "11:00", "disponible": False}
                    ]
                }
            ]
        }
    ]

    return render_template(
        "admin/dashboards/disponibilidad_consultorio.html",
        pisos=pisos,
        fecha=fecha
    )