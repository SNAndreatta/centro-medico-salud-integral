from flask import Blueprint, render_template, request, redirect, url_for

usuario_routes = Blueprint('rutas_admin_usuario', __name__)

# =================================
# DATOS SIMULADOS DE USUARIOS
# =================================

roles = [
    {"id": 1, "nombre": "RECEPCIONISTA"},
    {"id": 2, "nombre": "ADMIN"}
]


usuarios = [
    {
        "id": 1,
        "nombre": "Camila",
        "apellido": "Núñez",
        "nombre_completo": "Camila Núñez",
        "iniciales": "CN",
        "rol": "RECEPCIONISTA",
        "id_rol": 1,
        "mail": "camila@gmail.com",
        "fecha_nacimiento": "1990-05-12",
        "dni": "12345678",
        "color": "bg-pink-500/30 text-pink-500"
    },
    {
        "id": 2,
        "nombre": "Nicolás",
        "apellido": "Castro",
        "nombre_completo": "Nicolás Castro",
        "iniciales": "NC",
        "rol": "RECEPCIONISTA",
        "id_rol": 1,
        "mail": "nicolas@gmail.com",
        "fecha_nacimiento": "1988-03-20",
        "dni": "23456789",
        "color": "bg-green-500/30 text-green-500"
    },
    {
        "id": 3,
        "nombre": "Natalia",
        "apellido": "Gómez",
        "nombre_completo": "Natalia Gómez",
        "iniciales": "NG",
        "rol": "ADMIN",
        "id_rol": 2,
        "mail": "natalia@gmail.com",
        "fecha_nacimiento": "1992-07-15",
        "dni": "34567890",
        "color": "bg-slate-500/30 text-slate-500"
    },
    {
        "id": 4,
        "nombre": "Nicolás",
        "apellido": "Pérez",
        "nombre_completo": "Nicolás Pérez",
        "iniciales": "NP",
        "rol": "ADMIN",
        "id_rol": 2,
        "mail": "nicolas.perez@gmail.com",
        "fecha_nacimiento": "1985-11-08",
        "dni": "45678901",
        "color": "bg-lime-500/30 text-lime-500"
    },
    {
        "id": 5,
        "nombre": "Marcos",
        "apellido": "López",
        "nombre_completo": "Marcos López",
        "iniciales": "ML",
        "rol": "RECEPCIONISTA",
        "id_rol": 1,
        "mail": "marcos@gmail.com",
        "fecha_nacimiento": "1995-01-25",
        "dni": "56789012",
        "color": "bg-amber-500/30 text-amber-500"
    },
    {
        "id": 6,
        "nombre": "Cristian",
        "apellido": "Rosemary",
        "nombre_completo": "Marcos López",
        "iniciales": "CR",
        "rol": "RECEPCIONISTA",
        "id_rol": 2,
        "mail": "marcos@gmail.com",
        "fecha_nacimiento": "1995-01-25",
        "dni": "56789012",
        "color": "bg-indigo-500/30 text-indigo-500"
    },
    {
        "id": 7,
        "nombre": "Nicolás",
        "apellido": "Peace",
        "nombre_completo": "Marcos López",
        "iniciales": "NP",
        "rol": "ADMIN",
        "id_rol": 1,
        "mail": "marcos@gmail.com",
        "fecha_nacimiento": "1995-01-25",
        "dni": "56789012",
        "color": "bg-emerald-500/30 text-emerald-500"
    },
    {
        "id": 8,
        "nombre": "Lionel",
        "apellido": "Cabra",
        "nombre_completo": "Marcos López",
        "iniciales": "LC",
        "rol": "ADMIN",
        "id_rol": 1,
        "mail": "marcos@gmail.com",
        "fecha_nacimiento": "1995-01-25",
        "dni": "56789012",
        "color": "bg-teal-500/30 text-teal-500"
    },
]


# =================================
# MOSTRAR USUARIOS
# =================================

@usuario_routes.route("/usuarios")
def usuarios_index():

    return render_template(
        "admin/abm/usuarios/index.html",
        usuarios=usuarios,
        roles=roles
    )


# =================================
# CREAR USUARIO
# =================================

@usuario_routes.route("/usuarios/crear", methods=["POST"])
def crear_usuario():

    nombre = request.form.get("nombre", "").strip()
    apellido = request.form.get("apellido", "").strip()
    mail = request.form.get("mail", "").strip()
    fecha_nacimiento = request.form.get("fecha_nacimiento", "")
    dni = request.form.get("dni", "").strip()
    id_rol = request.form.get("id_rol", type=int)

    # Buscar el rol seleccionado
    rol_seleccionado = next(
        (rol for rol in roles if rol["id"] == id_rol),
        None
    )

    if not nombre or not apellido or not mail or not fecha_nacimiento or not dni or rol_seleccionado is None:
        return redirect(url_for("usuarios_index"))

    # Generar ID
    nuevo_id = max((usuario["id"] for usuario in usuarios), default=0) + 1

    # Generar iniciales
    iniciales = nombre[0].upper() + apellido[0].upper()

    # Colores de avatar
    colores = [
        ("#F8DCE1", "#E66D85"),
        ("#DDF1F1", "#60BFC1"),
        ("#E9D9ED", "#A66BAF"),
        ("#F1BDBD", "#B91C1C"),
        ("#B9CAD5", "#073B57")
    ]

    color, color_texto = colores[(nuevo_id - 1) % len(colores)]

    # Crear usuario
    nuevo_usuario = {
        "id": nuevo_id,
        "nombre": nombre,
        "apellido": apellido,
        "nombre_completo": nombre + " " + apellido,
        "iniciales": iniciales,
        "rol": rol_seleccionado["nombre"],
        "id_rol": id_rol,
        "mail": mail,
        "fecha_nacimiento": fecha_nacimiento,
        "dni": dni,
        "color": color,
        "color_texto": color_texto
    }

    usuarios.append(nuevo_usuario)

    return redirect(url_for("usuarios_index"))