import logging
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.config import Config

logger = logging.getLogger(__name__)


def generar_token_cancelacion_turno(id_turno, id_paciente):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps({
        'id_turno': int(id_turno),
        'id_paciente': int(id_paciente),
        'tipo': 'cancelacion_turno',
    })


def validar_token_cancelacion_turno(token):
    if not token or not token.strip():
        raise ValueError('Se requiere un token de cancelación válido')

    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        payload = serializer.loads(token, max_age=Config.CANCELACION_TTL_MINUTES * 60)
    except (BadSignature, SignatureExpired) as exc:
        raise ValueError('El enlace de cancelación es inválido o expiró') from exc

    if payload.get('tipo') != 'cancelacion_turno':
        raise ValueError('El token no corresponde a una cancelación de turno')

    if int(payload.get('id_turno', -1)) <= 0 or int(payload.get('id_paciente', -1)) <= 0:
        raise ValueError('El token de cancelación es inválido')

    return payload


def _crear_servidor_smtp():
    if not Config.SMTP_ENABLED:
        raise RuntimeError('SMTP está deshabilitado en la configuración')

    if Config.SMTP_USE_SSL:
        servidor = smtplib.SMTP_SSL(
            Config.SMTP_SERVER,
            Config.SMTP_PORT,
            timeout=Config.SMTP_TIMEOUT,
        )
    else:
        servidor = smtplib.SMTP(
            Config.SMTP_SERVER,
            Config.SMTP_PORT,
            timeout=Config.SMTP_TIMEOUT,
        )
        if Config.SMTP_USE_TLS:
            servidor.starttls()

    if Config.SMTP_USERNAME and Config.SMTP_PASSWORD:
        servidor.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)

    return servidor


def _formatear_fecha(fecha_horario):
    if not fecha_horario:
        return 'Sin fecha'
    if isinstance(fecha_horario, str):
        return fecha_horario
    return fecha_horario.strftime('%d/%m/%Y %H:%M hs')


def generar_url_cancelacion_turno(id_turno, id_paciente):
    token = generar_token_cancelacion_turno(id_turno, id_paciente)
    base_url = Config.PUBLIC_BASE_URL.rstrip('/')
    return f'{base_url}/api/turnos/{id_turno}/cancelar?token={token}'


def enviar_comprobante_turno(turno, paciente, qr_bytes, mime_type='image/png'):
    if not paciente or not paciente.get('correo_electronico'):
        logger.warning('No se envía comprobante porque no existe correo del paciente')
        return {'enviado': False, 'motivo': 'SIN_CORREO'}

    if not Config.SMTP_ENABLED:
        logger.info('SMTP deshabilitado; el comprobante no se envía')
        return {'enviado': False, 'motivo': 'SMTP_DESHABILITADO'}

    email_destino = paciente['correo_electronico'].strip()
    try:
        mensaje = MIMEMultipart('related')
        mensaje['Subject'] = 'Comprobante de turno - Centro Médico Salud Integral'
        mensaje['From'] = Config.SMTP_DEFAULT_SENDER
        mensaje['To'] = email_destino

        nombre_paciente = (
            f"{paciente.get('nombre', '').strip()} {paciente.get('apellido', '').strip()}"
        ).strip() or 'Paciente'
        nombre_medico = (
            f"{turno.get('medico', {}).get('nombre', '').strip()} "
            f"{turno.get('medico', {}).get('apellido', '').strip()}"
        ).strip() or 'Médico'
        especialidad = turno.get('medico', {}).get('especialidad', 'Consulta')
        fecha_turno = _formatear_fecha(turno.get('fecha_horario_inicial'))
        cancel_url = generar_url_cancelacion_turno(turno['id_turno'], paciente['id_paciente'])

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f5f8fb; padding: 24px; color: #1f2937;">
            <div style="max-width: 640px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.06);">
              <h2 style="margin-top: 0; color: #0f172a;">Comprobante de turno</h2>
              <p>Hola <strong>{nombre_paciente}</strong>,</p>
              <p>Te confirmamos tu turno en Centro Médico Salud Integral.</p>

              <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                  <td style="padding: 8px 0; color: #475569;">Especialidad</td>
                  <td style="padding: 8px 0; font-weight: 600;">{especialidad}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; color: #475569;">Médico</td>
                  <td style="padding: 8px 0; font-weight: 600;">{nombre_medico}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; color: #475569;">Fecha y horario</td>
                  <td style="padding: 8px 0; font-weight: 600;">{fecha_turno}</td>
                </tr>
                <tr>
                  <td style="padding: 8px 0; color: #475569;">Consultorio</td>
                  <td style="padding: 8px 0; font-weight: 600;">{turno.get('consultorio', {}).get('numero', 'N/D')} - Piso {turno.get('consultorio', {}).get('piso', 'N/D')}</td>
                </tr>
              </table>

              <div style="text-align: center; margin: 24px 0;">
                <img src="cid:qr_turno" alt="Código QR del turno" style="width: 180px; height: 180px; border: 1px solid #dbe2ea; border-radius: 8px; background: white;" />
              </div>

              <p style="margin-bottom: 18px;">Podés presentar este comprobante en recepción o escanear el código QR para registrar tu llegada.</p>

              <p style="margin: 18px 0;">
                <a href="{cancel_url}" style="display: inline-block; background-color: #dc2626; color: white; text-decoration: none; padding: 12px 18px; border-radius: 8px; font-weight: 700;">
                  Cancelar reserva
                </a>
              </p>

              <p style="font-size: 12px; color: #64748b;">Si no podés cancelar desde el correo, podés acercarte a recepción o usar el enlace de cancelación proporcionado.</p>
            </div>
          </body>
        </html>
        """

        mensaje.attach(MIMEText(html, 'html'))

        imagen_qr = MIMEImage(qr_bytes, _subtype='png')
        imagen_qr.add_header('Content-ID', '<qr_turno>')
        imagen_qr.add_header('Content-Disposition', 'inline', filename='qr_turno.png')
        mensaje.attach(imagen_qr)

        with _crear_servidor_smtp() as servidor:
            servidor.send_message(mensaje)

        logger.info('Correo de comprobante enviado correctamente a %s', email_destino)
        return {'enviado': True, 'destinatario': email_destino}
    except (smtplib.SMTPException, OSError, ValueError) as exc:
        logger.exception('Error al enviar comprobante por SMTP para %s', email_destino)
        return {'enviado': False, 'motivo': 'ERROR_ENVIO', 'error': str(exc)}
