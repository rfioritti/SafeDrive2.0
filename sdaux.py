from flask import Flask, request, jsonify
from datetime import datetime
import json
import time

from procesar_respuesta import perfilar_consulta
from guardadoDatos import guardar_recorrido
from prediccion_fatiga_distraccion import predecir_probabilidades_fatiga_distraccion
from firebase_admin import credentials, firestore, initialize_app

from generar_CSV_modelo import actualizar_csv_firebase
from ModeloDistraccionYSueno import crear_modelo

# Configura las credenciales de Firebase
cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
initialize_app(cred)
db = firestore.client()

def actualizar_modelo():
    actualizar_csv_firebase()
    crear_modelo()

app = Flask(__name__)

@app.route('/recibir_datos', methods=['POST'])
def recibir_datos():
    data = request.get_json()

    recorrido = perfilar_consulta(json.dumps(data))

    firebase_response = guardar_recorrido(recorrido, db)
    #print(firebase_response)
    dor, dist = predecir_probabilidades_fatiga_distraccion(recorrido)

    response_data = {"message": "Recorrido recibido, se envian las probabilidades de dormirse o distraerse.", "dor": int(dor*100), "dist": int(dist*100)}

    return jsonify(response_data)

if __name__ == '__main__':
    # Para despliegues de producción, cambiar a:
    # app.run(host='0.0.0.0', port=2225)
    app.run(host='0.0.0.0', port=2225, debug=True)
