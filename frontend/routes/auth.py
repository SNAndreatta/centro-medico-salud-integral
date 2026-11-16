
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
        nro_afiliado = request.form.get('nro_afiliado', '').strip()

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
                coberturas=[],
                id_cobertura='',
                nro_afiliado=''
            )

        if password != confirmar_password:
            return render_template(
                'auth/register.html',
                mensaje='Las contraseñas no coinciden.',
                coberturas=[],
                id_cobertura='',
                nro_afiliado=''
            )

        datos = {
            'nombre': nombre,
            'apellido': apellido,
            'dni': dni,
            'correo_electronico': correo_electronico,
            'fecha_nacimiento': fecha_nacimiento,
            'password': password,
            'id_cobertura': id_cobertura if id_cobertura else None,
            'nro_afiliado': nro_afiliado if nro_afiliado else None
        }

        # Validar que id_cobertura y nro_afiliado vayan juntos
        if id_cobertura and not nro_afiliado:
            return render_template(
                'auth/register.html',
                mensaje='Si seleccionás una cobertura, también ingresá el número de afiliado.',
                coberturas=[],
                id_cobertura='',
                nro_afiliado=''
            )

        if nro_afiliado and not id_cobertura:
            return render_template(
                'auth/register.html',
                mensaje='Para ingresar nro. de afiliado también debés seleccionar una cobertura.',
                coberturas=[],
                id_cobertura='',
                nro_afiliado=''
            )

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
                    mensaje=mensaje
                )

            return redirect(url_for('rutas_auth.login'))

        except requests.RequestException:
            return render_template(
                'auth/register.html',
                mensaje='No se pudo conectar con el servidor.'
            )

    try:
        coberturas_resp = requests.get(
            f"{current_app.config['BACKEND_URL']}/coberturas",
            timeout=10
        ).json()
        coberturas = coberturas_resp.get('coberturas', [])
    except Exception:
        coberturas = []

    return render_template(
        'auth/register.html',
        coberturas=coberturas
    )


# LOGOUT
@auth_routes.route('/logout', methods=['GET', 'POST'])
def logout():

    session.clear()

    return redirect(url_for('rutas_auth.login'))
