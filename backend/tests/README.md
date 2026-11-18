# Pruebas de regresión: coberturas y agendas

Usan `unittest` de Python y las dependencias existentes del backend.

Desde la carpeta `backend`:

```powershell
python -m unittest discover -s tests -v
```

Sin una base de pruebas configurada se ejecutan las validaciones de horarios y
se omiten explícitamente las pruebas de integración.

Para probar las operaciones con MySQL:

1. Crear una base **desechable**, cuyo nombre comience con `test_`.
2. Ejecutar allí `database/init_db.sql` y `database/seed.sql`.
3. Configurar en la terminal `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
   `DB_PASSWORD` y `SECRET_KEY` para ese entorno. No usar la base habitual ni
   guardar credenciales en el repositorio.
4. Ejecutar el mismo comando anterior.

Las pruebas de integración usan la cuenta administradora de demostración del
seed, comprueban las respuestas de Flask y consultan MySQL para verificar los
cambios. Crean y limpian sus coberturas y agendas. Deben ejecutarse sin
otros procesos modificando esa base desechable.

## Casos cubiertos

- **#65:** borrado efectivo de coberturas sin uso; desaparición del
  listado; segundo borrado con 404; rechazo con 409 y conservación de datos si
  hay pacientes o médicos asociados.
- **#66:** rechazo de offsets positivos, negativos, UTC y `Z` tanto al inicio
  como al fin; ninguna fila creada por esas peticiones; aceptación y persistencia
  de horas locales; conservación de errores de rango y duración de jornada.
