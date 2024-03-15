from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import ssl
from email.message import EmailMessage

import random
import string

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Configurar el servidor SMTP
SERVER = 'smtp.gmail.com'
PORT = 465
CONTEXT = ssl.create_default_context()
USERNAME = 'seterisparibus2019@gmail.com'  # Reemplaza con tu dirección de correo electrónico
PASSWORD = 'jdnjkyfarmdglfds'  # Reemplaza con tu contraseña de correo electrónico

pending_logins = {}

def send_email(to_email, subject, content):
    em = EmailMessage()
    em['From'] = USERNAME
    em['To'] = to_email
    em['subject'] = subject
    em.set_content(content)

    with smtplib.SMTP_SSL(SERVER, PORT, CONTEXT) as smtp:
        smtp.login(USERNAME, PASSWORD)
        smtp.sendmail(USERNAME, to_email, em.as_string())

@app.route('/sendCode', methods=['POST'])
def send_code():
    data = request.json
    email = data['email']
    verification_code = ''.join(random.choices(string.digits, k=8))  # Genera un código de 8 dígitos

    pending_logins[email] = verification_code

    print(pending_logins[email])
    print(email)

    try:
        send_email(email, 'Código de verificación', f'Tu código de verificación es: {verification_code}')
        return 'Código de verificación enviado por correo electrónico.', 200
    except Exception as e:
        print(f'Error al enviar el código de verificación por correo electrónico: {e}')  # Imprimir la excepción completa
        return 'Error al enviar el código de verificación por correo electrónico.', 500

@app.route('/verifyCode', methods=['POST'])
def verify_code():
    data = request.json
    code = data['code']
    email = data['email']

    if code == pending_logins[email]:
        del pending_logins[email]
        return 'Código de verificación válido.', 200
    else:
        return 'Código de verificación inválido.', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5557, debug=True)