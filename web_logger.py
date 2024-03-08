from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string

app = Flask(__name__)
CORS(app)

# Configurar el servidor SMTP
SMTP_SERVER = 'adinet.com.uy'
SMTP_PORT = 25
SMTP_USERNAME = 'rjff@vera.com.uy'  # Reemplaza con tu dirección de correo electrónico
SMTP_PASSWORD = 'rjff13'  # Reemplaza con tu contraseña de correo electrónico

pending_logins = {}

def send_email(to_email, subject, content):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
    server.quit()

@app.route('/sendCode', methods=['POST'])
def send_code():
    data = request.json
    email = data['email']
    verification_code = ''.join(random.choices(string.digits, k=8))  # Genera un código de 8 dígitos

    pending_logins[email] = verification_code

    try:
        send_email(email, 'Código de verificación', f'Tu código de verificación es: {verification_code}')
        return 'Código de verificación enviado por correo electrónico.', 200
    except Exception as e:
        print(e)
        return 'Error al enviar el código de verificación por correo electrónico.', 500

@app.route('/verifyCode', methods=['POST'])
def verify_code():
    data = request.json
    code = data['code']
    email = data['email']

    # Aquí puedes realizar la lógica para verificar el código
    # Por ejemplo, puedes compararlo con un código generado previamente y almacenado en tu base de datos

    # Simplemente para este ejemplo, asumimos que el código es correcto si es '12345678'
    if code == pending_logins[email]:
        del pending_logins[email]
        return 'Código de verificación válido.', 200
    else:
        return 'Código de verificación inválido.', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5557, debug=True)