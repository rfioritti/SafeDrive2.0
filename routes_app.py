from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/receive_markers', methods=['POST'])
def receive_markers():
    try:
        markers_json = request.get_json()

        print('MarkersJSON recibido:', markers_json)

        # Realizar alguna lógica con los datos recibidos si es necesario

        response_data = {'status': 'success', 'message': 'Información recibida correctamente'}
        return jsonify(response_data), 200
    except Exception as e:
        print(f'Error al procesar los datos: {str(e)}')
        response_data = {'status': 'error', 'message': f'Error al procesar los datos: {str(e)}'}
        return jsonify(response_data), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
