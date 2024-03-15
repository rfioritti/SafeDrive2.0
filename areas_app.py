from flask import Flask, request, jsonify
from flask_cors import CORS
from analisis_zona import obtener_nivel_riesgo
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
CORS(app)

# Configura las credenciales de Firebase
cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
initialize_app(cred)
db = firestore.client()

@app.route('/receive_area', methods=['POST'])
def receive_area():
    try:
        markers_json = request.get_json()

        #print('MarkersJSON recibido:', markers_json)

        deptos = markers_json.pop('deptos', [])

        map_results = obtener_nivel_riesgo(markers_json, deptos, db)

        #print(map_results)



        response_data = {'status': 'success', 'message': 'Información recibida correctamente', 'results': map_results}
        return jsonify(response_data), 200
    except Exception as e:
        print(f'Error al procesar los datos: {str(e)}')
        response_data = {'status': 'error', 'message': f'Error al procesar los datos: {str(e)}'}
        return jsonify(response_data), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5556, debug=True)