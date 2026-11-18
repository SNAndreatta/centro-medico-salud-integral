
import requests

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
    jsonify
)

auth_routes = Blueprint('rutas_auth', __name__)


ROLES = {
    1: 'administrador',
    2: 'recepcionista',
    3: 'paciente',
    4: 'medico',
}


def _listar_coberturas():
    """Coberturas de la base de datos para el selector del registro.

    Devuelve una lista vacía si el backend no está disponible, para que el
    registro siga funcionando con la opción "Particular".
    """
    try:
        respuesta = requests.get(
            f"{current_app.config['BACKEND_URL']}/coberturas",
            timeout=10
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
    except (requests.RequestException, ValueError):
        return []

    return [
        {
            'id': cobertura.get('id_cobertura'),
            'nombre': cobertura.get('nombre'),
        }
        for cobertura in datos.get('coberturas', [])
        if cobertura.get('id_cobertura') and cobertura.get('nombre')
    ]


# LOGIN
@auth_routes.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        correo_electronico = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not correo_electronico or not password:
            return render_template(
                'auth/login.html',
                mensaje='Completá todos los campos.'
            )

        try:
            respuesta = requests.post(
                f"{current_app.config['BACKEND_URL']}/auth/login",
                json={
                    'correo_electronico': correo_electronico,
                    'password': password
                },
                timeout=10
            )

            try:
                datos = respuesta.json()
            except ValueError:
                datos = {}

            if respuesta.status_code != 200:
                return render_template(
                    'auth/login.html',
                    mensaje=datos.get(
                        'mensaje',
                        'Correo electrónico o contraseña incorrectos.'
                    )
                )

            usuario = datos.get('usuario')
            print("LOGIN USUARIO:", usuario, flush=True)
            access_token = datos.get('access_token')

            if not usuario or not access_token:
                return render_template(
                    'auth/login.html',
                    mensaje='El servidor devolvió una respuesta incompleta.'
                )

            id_rol = usuario.get('id_rol')

            session.clear()
            session['access_token'] = access_token
            session['usuario'] = usuario
            session['id_usuario'] = usuario.get('id_usuario')
            session['id_rol'] = id_rol
            session['rol'] = ROLES.get(id_rol, 'paciente')
            session['nombre'] = usuario.get('nombre', '')
            session['apellido'] = usuario.get('apellido', '')

            return redirect(url_for('rutas_home.home'))

        except requests.RequestException:
            return render_template(
                'auth/login.html',
                mensaje='No se pudo conectar con el servidor.'
            )

    return render_template('auth/login.html')


# REGISTRO
@auth_routes.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        nombre = request.form.get('first_name', '').strip()
        apellido = request.form.get('last_name', '').strip()
        dni = request.form.get('dni', '').strip()
        correo_electronico = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirmar_password = request.form.get('confirm_password', '')
        fecha_nacimiento = request.form.get('fecha_nacimiento', '').strip()
        id_cobertura = request.form.get('id_cobertura', '').strip()

        if not all([
            nombre,
            apellido,
            dni,
            correo_electronico,
            password,
            confirmar_password,
            fecha_nacimiento
        ]):
            return render_template(
                'auth/register.html',
                mensaje='Completá todos los campos.',
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

        if password != confirmar_password:
            return render_template(
                'auth/register.html',
                mensaje='Las contraseñas no coinciden.',
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

        # El nro. de afiliado NO se pide: el backend lo genera automáticamente
        # cuando el paciente elige una cobertura.
        cobertura_id = None
        if id_cobertura:
            try:
                cobertura_id = int(id_cobertura)
            except ValueError:
                return render_template(
                    'auth/register.html',
                    mensaje='La cobertura seleccionada no es válida.',
                    coberturas=_listar_coberturas(),
                    id_cobertura=''
                )

        datos = {
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni,
            'correo_electronico': correo_electronico,
            'fecha_nacimiento': fecha_nacimiento,
            'password': password,
            'id_cobertura': cobertura_id,
        }

        try:
            respuesta = requests.post(
                f"{current_app.config['BACKEND_URL']}/pacientes",
                json=datos,
                timeout=10
            )

            try:
                resultado = respuesta.json()
            except ValueError:
                resultado = {}

            if respuesta.status_code != 201:

                print("ERROR EN REGISTRO:")
                print("Estado:", respuesta.status_code)
                print("Respuesta del backend:", respuesta.text)

                errores = resultado.get('errors')
                mensaje_backend = None

                if isinstance(errores, list) and errores:
                    primer_error = errores[0]

                    if isinstance(primer_error, dict):
                        mensaje_backend = (
                            primer_error.get('message')
                            or primer_error.get('description')
                        )

                mensaje = (
                    resultado.get('mensaje')
                    or mensaje_backend
                    or resultado.get('error')
                    or resultado.get('detalle')
                    or 'No se pudo crear la cuenta. Revisá los datos e intentá nuevamente.'
                )

                return render_template(
                    'auth/register.html',
                    mensaje=mensaje,
                    coberturas=_listar_coberturas(),
                    id_cobertura=id_cobertura
                )

            return redirect(url_for('rutas_auth.login'))

        except requests.RequestException:
            return render_template(
                'auth/register.html',
                mensaje='No se pudo conectar con el servidor.',
                coberturas=_listar_coberturas(),
                id_cobertura=id_cobertura
            )

    return render_template(
        'auth/register.html',
        coberturas=_listar_coberturas(),
        id_cobertura=''
    )


# LOGOUT
@auth_routes.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()

    return redirect(url_for('rutas_auth.login'))
