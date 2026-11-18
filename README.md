# Centro medico salud integral

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

## Desarrollo
Antes de iniciar los contenedores, crear el archivo de configuración del backend y completar `SECRET_KEY` con una clave aleatoria:

```bash
cp backend/.env.template backend/.env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar el valor generado en `backend/.env`. El backend acepta una clave de desarrollo solo cuando `FLASK_DEBUG=true`; en modo no-debug exige una clave de al menos 32 caracteres.

Para habilitar el envío de comprobantes por email, completar también las variables SMTP del archivo `backend/.env` con la cuenta del proveedor y el host seguro (por ejemplo Gmail, SMTP de la empresa o un relay corporativo). Las opciones `SMTP_USE_TLS`/`SMTP_USE_SSL` controlan la conexión segura, y el envío queda deshabilitado por defecto si `SMTP_ENABLED=false`.

Para ejecutar la db mysql local usar 
``` bash
docker compose -f docker-compose.yaml -f docker-compose.development.yaml --profile development up --build
```
