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

Antes de iniciar los contenedores, crear el archivo de configuración del backend:

```bash
cp backend/.env.template backend/.env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar la clave generada en `SECRET_KEY` dentro de `backend/.env`. El backend exige una clave segura en modo producción y acepta una clave de desarrollo solo con `FLASK_DEBUG=true`.

Para habilitar el envío de comprobantes por email, completar en `backend/.env`:

- `SMTP_ENABLED=true`.
- `SMTP_SERVER` y `SMTP_PORT`.
- `SMTP_USERNAME` y `SMTP_PASSWORD`.
- `SMTP_USE_TLS` o `SMTP_USE_SSL` según el proveedor.
- `SMTP_DEFAULT_SENDER`.
- `PUBLIC_BASE_URL` con la URL pública del backend.

El envío permanece deshabilitado por defecto si `SMTP_ENABLED=false`.

El proyecto utiliza `America/Argentina/Buenos_Aires` como zona horaria. La fecha local se obtiene mediante las utilidades existentes en lugar de usar el reloj o la fecha del contenedor.

## Ejecución con Docker

Desde la raíz del proyecto:

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
