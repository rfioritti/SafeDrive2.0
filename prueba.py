import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def enviar_correo(destinatario, asunto, mensaje):
    # Configuración del servidor SMTP
    servidor_smtp = 'smtp.gmail.com'  # Aquí debes usar el servidor SMTP que corresponda
    puerto_smtp = 587  # Puerto SMTP
    remitente = 'seterisparibus2019@gmail.com'  # Dirección de correo electrónico del remitente
    contraseña = 'jdnjkyfarmdglfds'  # Contraseña del remitente

    # Crear el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Agregar el cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))

    # Iniciar la conexión con el servidor SMTP
    server = smtplib.SMTP(host=servidor_smtp, port=puerto_smtp)
    server.starttls()  # Habilitar el cifrado TLS

    # Iniciar sesión en el servidor SMTP
    server.login(remitente, contraseña)

    # Enviar el correo electrónico
    server.sendmail(remitente, destinatario, msg.as_string())

    # Cerrar la conexión con el servidor SMTP
    server.quit()

# Ejemplo de uso
destinatario = '99agusterra@gmail.com'
asunto = 'Prueba de correo electrónico'
mensaje = 'Este es un mensaje de prueba.'
enviar_correo(destinatario, asunto, mensaje)