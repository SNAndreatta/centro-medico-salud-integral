# AGENTS.md

Centro médico "Salud Integral": monorepo con **API Flask** (`backend/`, puerto 5000), **web Flask server-side-rendered** (`frontend/`, puerto 8000) y **MySQL 8.4** (`db`, puerto 3306).

## Arquitectura (lo que no se deduce de los nombres)

- `backend/app.py` monta **todas** sus rutas bajo el prefijo `/api` (`DispatcherMiddleware`). Contrato de API en `docs/swagger.yaml`.
- `frontend/` **no toca la base**: todo pasa por `frontend/src/api.py::api()`, que reenvía el JWT de `session['access_token']` (`Authorization: Bearer`) a `BACKEND_URL` (por defecto `http://api:5000/api`) y levanta `ErrorAPI(mensaje, status)` si la API falla.
- Login: `frontend/routes/auth.py` guarda en sesión `access_token`, `usuario`, `id_usuario`, `id_rol`, `rol` (`administrador|recepcionista|medico|paciente`), `nombre`, `apellido`. El control de acceso del frontend usa alias (`admin`, `recepcion`) en `frontend/src/permisos.py`.
- Capas del backend: `routes` (HTTP) → `services` (reglas) → `repositories` (SQL) → `src/db.py::obtener_cursor()`. Los errores de negocio usan `src/errores.py::error_respuesta(mensaje, codigo)` y se devuelven como `{"errors":[{code,message,...}]}`.
- Roles: 1 administrador, 2 recepcionista, 3 paciente, 4 médico (`backend/src/utils/roles.py`).

## Comandos

```bash
# Stack completo (MySQL está en el profile "development": sin esto NO levanta la db)
docker compose -f docker-compose.yaml -f docker-compose.development.yaml --profile development up --build

# Cambios en backend/app.py  -> la imagen NO tiene volume mount: hay que rebuild
docker compose up -d --build api

# Cambios en frontend/       -> volume mount + FLASK_DEBUG=true: se recarga solo
docker compose restart frontend

# Tests backend (unittest con pytest como runner: 36 passed / 5 skipped)
cd backend && ../venv/bin/python -m pytest tests/ -q
cd backend && ../venv/bin/python -m pytest tests/test_turnos_estado_medico.py -q   # archivo puntual

# Tests frontend (pytest + Flask test_client; parchea routes.<modulo>.api)
cd frontend && PYTHONPATH=/tmp/opencode/pydeps:. ../venv/bin/python -m pytest tests/ -q
#   OJO: el venv de la raíz NO tiene `requests` (lo importan src/api.py y routes/auth.py).
#   Instalalo con `../venv/bin/python -m pip install -r requirements.txt` y corré sin PYTHONPATH.

# CSS (Tailwind v4). El output.css commiteado va SIN minificar: usá este comando,
# no `npm run build` (ese agrega --minify y cambia todo el archivo).
npx @tailwindcss/cli -i ./frontend/static/css/input.css -o ./frontend/static/css/output.css

# JS: chequeo de sintaxis
node --check frontend/static/js/mis_turnos.js

# SQL directo contra la db del container
docker exec centro-medico-db mysql -uapp_user -papp_password centro_medico -e "SELECT ...;"
```

- `backend/app.py` ejecuta `database/initdb.sh` al arrancar: aplica `init_db.sql` (`CREATE TABLE IF NOT EXISTS`) y `seed.sql` (`INSERT IGNORE`). Es idempotente, **no borra datos**.
- El `api` corre con `FLASK_DEBUG=false`; el `frontend` con `FLASK_DEBUG=true`.

## Reglas de negocio (fáciles de romper)

- **Estados de turno** (`estado_turno`): 1 disponible, 2 reservado, 3 confirmado, 4 atendido, 5 cancelado, 6 ausente.
- **Check-in por QR**: `POST /turnos/checkin` (admin/recepción) acepta el token sólo dentro de **[hora_turno − 30 min, hora_turno + 15 min]** y sólo desde `reservado` → `confirmado`. El token es un payload JSON en base64url; se genera al reservar.
- **`PUT /turnos/<id>/estado`** acepta `{"estado": "atendido"}` (nombre) o `{"id_estado": 4}` (id). Destinos válidos: `atendido` y `ausente`. Para `atendido` el turno debe estar **confirmado** y dentro de la ventana de jornada (**1 h antes → 12 h después** del horario del turno; si no, 409 `TURNO_FUERA_DE_RANGO`). Con rol MEDICO sólo se pueden tocar turnos de la propia agenda (403 `TURNO_NO_AUTORIZADO`).
- **Agendas**: `dia_semana` es ISO (**1 = lunes … 7 = domingo**). Los slots se generan desde `hora_inicio` mientras `inicio + duracion <= hora_fin`.
- **Disponibilidad**: `POST /turnos/generar` sólo se habilita **desde el día 15** del mes y genera para el mes siguiente (409 `APERTURA_AGENDA_NO_HABILITADA`).
- **Cancelación por el paciente**: hasta 24 h antes del turno (409 `CANCELACION_FUERA_DE_PLAZO`).

## Zona horaria (el bug que costó tiempo)

Todo el sistema es **America/Argentina/Buenos_Aires** (`TZ`/`TIMEZONE` en `docker-compose.yaml` y `backend/.env`).

- Backend: usá `backend/src/utils/fechas.py` (`ahora_local`, `hoy_local`). En SQL **no uses `CURDATE()`/`NOW()`** para "hoy": pasá la fecha local como parámetro (si no, el resultado depende de la TZ del contenedor MySQL).
- Frontend: usá `frontend/src/tiempo.py` (`ahora_local`, `hoy_local`). `datetime.now()`/`date.today()` en crudo comparan contra horarios del backend y marcan turnos de hoy como pasados.

## Frontend: quirks

- Tailwind v4 con `@source "../../templates"`, `"../js"` y **`"../../routes"`**: las clases que defines dentro de los `.py` de `routes/` también entran al CSS. Si agregás una clase Tailwind en un `.py`, **recompilá `output.css`** o no se va a ver.
- `frontend/static/css/input.css` aplica `html { zoom: 1.5 }` y breakpoints escalados ×1.5: la UI está diseñada para verse como un zoom del 150%. No lo "corrijás" sin pedirlo.
- `frontend/static/js/` es JS vanilla (sin framework); los modales y filtros viven en archivos por vista.
- `frontend/src/api_paciente.py` normaliza los payloads de la API a los diccionarios que usan los templates; `frontend/routes/agenda_mensual.py` es el helper de grilla mensual compartido por médico y admin.

## Cuentas demo (password `12345678`, de `backend/database/seed.sql`)

`admin.demo@`, `recepcion.demo@`, `paciente.demo@`, `medico.demo@` `@saludintegral.test`.
Médico demo: `id_usuario 104`, `id_medico 101`, agenda 101.

## Git

- Rama de trabajo: **`develop`** (hay otra worktree en `feature/millennial-ui`, no tocarla).
- Commits en español, estilo conventional commits (`feat(admin): ...`, `fix(backend): ...`, `test(frontend): ...`, `style: ...`).
- Convención pedida: **agrupar los commits por cambio lógico** y cerrar cada pedido con los `git add` + `git commit` + `git push origin develop`.
- En este sandbox **no hay credenciales de GitHub**: `git push` falla con `could not read Username for 'https://github.com'`. Dejá los commits listos y avisale al usuario que ejecute el push.

## Preferencia del usuario

**No cambiar colores, estética ni nada ajeno a lo pedido.** Si el cambio no lo requiere, no lo toques (ni CSS, ni templates, ni copy).
