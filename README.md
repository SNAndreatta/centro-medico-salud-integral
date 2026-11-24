# Centro Médico Salud Integral

Aplicación web para la gestión integral de turnos médicos: reserva por pacientes, administración de agendas y profesionales, control de llegada mediante códigos QR y seguimiento de ausentismo y ocupación.

## Integrantes
 
- Santino Nicolás Andreatta - 116024
- Galo Fernandez Achille - 116037
- Matias Mattos - 116125
- Lucio Pompei - 116611
- Valentina Carera - 116311
- Kiara Micaela Koo - 116282
- Lucía Saint Martin - 116324
- Joaquin Berzunces - 116175
- Nicolas Agustin Gonzalez Sanchez - 116641

## Resumen

Centro Médico Salud Integral fue desarrollado como Proyecto Integrador de Introducción al Desarrollo de Software. Reemplaza la administración manual de turnos por una plataforma con frontend, backoffice, backend, base de datos y procesos automatizados.

El sistema permite que los pacientes encuentren una especialidad y un médico, seleccionen un horario disponible y reciban por correo la confirmación junto con un código QR. Recepción puede registrar la llegada escaneando ese código. Administración y recepción gestionan los datos maestros, las agendas y los turnos, mientras que los médicos pueden consultar su agenda y marcar las consultas atendidas.

## Solución propuesta

### Pacientes

- Registro e inicio de sesión.
- Consulta del perfil.
- Reserva de turnos por especialidad, médico, día y horario.
- Recepción por correo de confirmación y QR. 
- Cancelación del turno mediante el enlace recibido.
- Consulta de turnos propios.

### Administración y recepción

- ABM de médicos, especialidades, consultorios, coberturas y pacientes.
- Configuración de agendas semanales o mensuales.
- Generación masiva de turnos disponibles.
- Gestión del estado de los turnos.
- Check-in de pacientes desde recepción.
- Consulta de sala de espera, ocupación y estadísticas.

### Médicos

- Vista de turnos propios.
- Consulta de la agenda del día.
- Cambio de turnos confirmados a atendido o ausente dentro de las reglas establecidas.

## Arquitectura

El proyecto está organizado como un monorepo con tres componentes principales:

- `backend/`: API Flask con rutas, servicios, repositorios y consultas SQL explícitas.
- `frontend/`: aplicación Flask SSR que no accede directamente a la base de datos.
- `db`: MySQL 8.4 ejecutado mediante Docker Compose en el entorno local.

La API monta sus rutas bajo el prefijo `/api`. El frontend comunica con la API desde Python mediante `frontend/src/api.py::api()`, que reenvía el JWT almacenado en la sesión y convierte los errores del backend en respuestas controladas.

La organización del backend sigue el flujo:

```text
routes → services → repositories → src/db.py → MySQL
```

No se utiliza un ORM. Las consultas se escriben directamente en SQL a través de cursores parametrizados.

Las validaciones de datos en services o routes se realizan con utilidades de validators o de utils.

## Tecnologías utilizadas

- Python 3 y Flask.
- MySQL 8.4.
- Docker y Docker Compose.
- HTML, Jinja y JavaScript vanilla.
- Tailwind CSS 4.
- PyJWT y Werkzeug para autenticación y contraseñas.
- Librerías `qrcode` y Pillow para códigos QR.
- Librería `requests` para la comunicación Python del frontend con la API.
- SMTP para comprobantes y confirmaciones por correo.
- Swagger y una colección Postman para documentar la API.

## Base de datos

Los scripts se encuentran en `backend/database/`:

- `init_db.sql`: crea las tablas si no existen.
- `seed.sql`: carga datos iniciales y cuentas de demostración.
- `initdb.sh`: aplica creación y carga inicial al iniciar el backend.

Las entidades principales incluyen usuarios, pacientes, médicos, especialidades, consultorios, coberturas, agendas, días de agenda y turnos. Los turnos y agendas utilizan fecha y hora como valores únicos de tipo `DATETIME` o `TIME` según corresponda a su significado.

Estados de turno:

| Estado | Identificador |
|---|---:|
| Disponible | 1 |
| Reservado | 2 |
| Confirmado | 3 |
| Atendido | 4 |
| Cancelado | 5 |
| Ausente | 6 |

## Roles y cuentas de demostración

Todas las cuentas demo utilizan la contraseña `12345678`.

| Rol | Usuario demo |
|---|---|
| Administrador | `admin.demo@saludintegral.test` |
| Recepcionista | `recepcion.demo@saludintegral.test` |
| Paciente | `paciente.demo@saludintegral.test` |
| Médico | `medico.demo@saludintegral.test` |

Los datos iniciales de las cuentas se encuentran en `backend/database/seed.sql`.

## Requisitos previos

- Docker.
- Docker Compose.
- Git.
- Puertos locales `8000`, `5000` y `3306` disponibles. El puerto 3306 no es necesario si se utiliza una base de datos hosteada.

## Configuración

El proyecto usa dos archivos de entorno separados: uno para la API y otro para el frontend. Docker Compose puede sobrescribir varias variables en el arranque de los contenedores.

### Configuración del backend

Crear el archivo de entorno:

```bash
cp backend/.env.template backend/.env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar la clave generada en `SECRET_KEY`.

#### Base de datos MySQL

| Variable | Descripción | Valor local recomendado |
|---|---|---|
| `DB_HOST` | Host donde escucha MySQL. Dentro de Docker Compose debe ser el nombre del servicio `db`. | `db` |
| `DB_PORT` | Puerto de MySQL. | `3306` |
| `DB_NAME` | Nombre de la base de datos. | `centro_medico` |
| `DB_USER` | Usuario con permisos sobre la base. | `app_user` |
| `DB_PASSWORD` | Contraseña del usuario de aplicación. | `app_password` |
| `DB_ROOT_PASSWORD` | Contraseña del usuario root usada al inicializar MySQL. | `root_password` |

El Compose ya sobrescribe `DB_HOST=db` y las demás variables desde el entorno raíz o desde los valores por defecto definidos en `docker-compose.yaml`. El archivo `backend/.env` debe conservar valores compatibles si se ejecuta el backend fuera de Docker.

#### Servidor Flask

| Variable | Descripción | Valor local recomendado |
|---|---|---|
| `FLASK_HOST` | Interfaz donde escucha la API. | `0.0.0.0` dentro de Docker; `127.0.0.1` fuera de Docker |
| `FLASK_PORT` | Puerto interno de la API. Compose lo publica como el puerto local elegido. | `5000` |
| `FLASK_DEBUG` | Activa el modo debug. Debe ser `true` solo para desarrollo. | `true` |
| `TIMEZONE` | Zona horaria usada por el backend. | `America/Argentina/Buenos_Aires` |

#### Seguridad y sesión

| Variable | Descripción | Valor recomendado |
|---|---|---|
| `SECRET_KEY` | Clave usada para Flask y JWT. Se genera una vez y debe mantenerse estable. | Clave aleatoria de al menos 32 caracteres |
| `JWT_ACCESS_TOKEN_MINUTES` | Duración del token de acceso en minutos. Debe ser un número mayor que cero. | `60` |

El backend acepta una clave de desarrollo si `FLASK_DEBUG=true`. En modo no-debug, `SECRET_KEY` es obligatoria y debe tener al menos 32 caracteres.

#### Correo SMTP

| Variable | Descripción | Valor inicial |
|---|---|---|
| `SMTP_ENABLED` | Habilita el envío de comprobantes y confirmaciones por correo. | `false` |
| `SMTP_SERVER` | Servidor SMTP del proveedor. | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP. Gmail normalmente utiliza `587` con TLS. | `587` |
| `SMTP_USE_TLS` | Usa STARTTLS. | `true` |
| `SMTP_USE_SSL` | Usa conexión SSL implícita. | `false` |
| `SMTP_USERNAME` | Usuario o dirección que inicia sesión en SMTP. | Vacío hasta configurar un proveedor |
| `SMTP_PASSWORD` | Contraseña o clave de aplicación SMTP. | Vacío hasta configurar un proveedor |
| `SMTP_DEFAULT_SENDER` | Remitente mostrado en los comprobantes. | `no-reply@saludintegral.local` |
| `SMTP_TIMEOUT` | Tiempo máximo de espera de una conexión SMTP, en segundos. | `15` |

Para activar el envío:

```env
SMTP_ENABLED=true
SMTP_USERNAME=cuenta@proveedor.test
SMTP_PASSWORD=clave-de-aplicacion
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

No usar la contraseña habitual de la cuenta si el proveedor exige una clave de aplicación. El envío queda deshabilitado si `SMTP_ENABLED=false`.

#### URLs y reglas temporales

| Variable | Descripción | Valor recomendado |
|---|---|---|
| `PUBLIC_BASE_URL` | URL pública usada para enlaces del backend incluidos en correos. | `http://localhost:5000` |
| `FRONTEND_URL` | URL del frontend usada al cancelar turnos o redirigir desde el backend. | `http://localhost:8000` |
| `CANCELACION_TTL_MINUTES` | Vigencia del token de cancelación, en minutos. Debe cubrir las 24 horas previas al turno. | `86400` |
| `INTERVALO_AUSENTISMO_SEGUNDOS` | Intervalo mínimo entre ejecuciones del control de ausentismo. | `300` |

### Configuración del frontend

El frontend lee las variables reales en `frontend/src/config.py`:

| Variable | Descripción | Valor recomendado |
|---|---|---|
| `FLASK_HOST` | Interfaz donde escucha el servidor Flask del frontend. | `0.0.0.0` dentro de Docker |
| `FLASK_PORT` | Puerto interno del frontend. Compose lo publica en `8000`. | `8000` |
| `FLASK_DEBUG` | Activa la recarga automática del frontend. | `true` |
| `TIMEZONE` | Debe coincidir con la zona horaria del backend. | `America/Argentina/Buenos_Aires` |
| `SECRET_KEY` | Clave de sesión del frontend. Debe ser estable y distinta de la clave del backend si se desea separarlas. | Clave aleatoria propia |
| `BACKEND_URL` | Dirección interna que usa Python `requests` para llamar a la API. Dentro de Docker debe apuntar al servicio `api`. | `http://api:5000/api` |

Docker Compose ya proporciona `FLASK_HOST`, `FLASK_PORT`, `FLASK_DEBUG`, `TIMEZONE` y `BACKEND_URL` usa su valor por defecto. En el template actual `frontend/.env.template` aparecen `FLASK_FRONT_HOST`, `FLASK_FRONT_PORT` y `FLASK_FRONT_DEBUG`; el código actual no lee esos nombres. Para configurar el frontend fuera de Docker se deben usar `FLASK_HOST`, `FLASK_PORT` y `FLASK_DEBUG`.

## Ejecución con Docker

Desde la raíz del proyecto para desarrollo:

```bash
docker compose -f docker-compose.yaml -f docker-compose.development.yaml --profile development up --build
```

URLs locales:

- Frontend: `http://localhost:8000`.
- API: `http://localhost:5000/api`.
- Estado de la API: `http://localhost:5000/api/health`.
- MySQL: `localhost:3306`.

Para detener los contenedores:

```bash
docker compose down
```

Después de modificar archivos del frontend, Flask Debug permite que el volumen se recargue automáticamente. Puede ser necesario reiniciar el servicio:

```bash
docker compose restart frontend
```

Los cambios en `backend/app.py` requieren reconstruir el contenedor de API:

```bash
docker compose up -d --build api
```

## API y documentación

La documentación OpenAPI se encuentra en `docs/swagger.yaml`. La colección de pruebas de Postman está en `docs/postman.json`.

Los módulos principales de la API incluyen autenticación, usuarios, pacientes, médicos, especialidades, consultorios, coberturas, agendas, turnos y estadísticas. Todos los endpoints protegidos requieren el JWT emitido por el proceso de autenticación.

## Reglas de negocio relevantes

- Los turnos de un médico no pueden solaparse.
- Un paciente no puede tener dos turnos activos simultáneos con el mismo médico.
- Un consultorio no puede quedar asignado a dos turnos simultáneos.
- Las agendas definen días, horarios, duración y consultorio asignado.
- Los slots se generan hasta respetar el horario de fin de la jornada.
- La cancelación del paciente se admite hasta 24 horas antes del turno.
- El check-in mediante QR se admite desde 30 minutos antes hasta 15 minutos después del turno.
- La llegada se registra una sola vez por turno.
- Un turno confirmado puede pasar a atendido dentro de la ventana definida por el sistema.
- Los turnos sin check-in quedan sujetos al procesamiento automático de ausentismo.
- La apertura de agendas genera los turnos del mes siguiente.

Los supuestos acordados para el proyecto están detallados en `docs/supuestos.txt`.

## Diseño responsive

Las interfaces utilizan Tailwind CSS con clases responsivas y vistas adaptables para computadoras, tablets y dispositivos móviles.

## Decisiones de diseño

- Se centralizó la configuración horaria en Argentina/Buenos Aires para evitar diferencias entre contenedores y datos SQL.
- Se implementaron ventanas temporales específicas para check-in, atención y cancelación.
- Se preservan las reservas canceladas como historial y se vuelve a ofrecer el horario disponible.
- Se usa una tarea y mecanismos de ejecución controlada, ejecutada previo a cada petición, para procesar ausentismos. Esto se debe a que a la hora de hostear la aplicación en Vercel las tareas programadas en flask no funcionan. Y además, las tareas programadas de Vercel están muy limitadas en el plan gratuito.
