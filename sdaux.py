import socket
import json
import time
from datetime import datetime
from procesar_respuesta import perfilar_consulta
from guardadoDatos import guardar_recorrido
from prediccion_fatiga_distraccion import predecir_probabilidades_fatiga_distraccion
from generar_CSV_modelo import actualizar_csv_firebase
from ModeloDistraccionYSueno import crear_modelo


def actualizar_modelo():
    
    actualizar_csv_firebase()
    crear_modelo()
    

# Configura el servidor
server_ip = '0.0.0.0'  # Escucha en todas las interfaces de red
server_port = 2225

# Crea un socket para escuchar conexiones entrantes
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)

print(f"Esperando conexiones en {server_ip}:{server_port}")

while True:
    # Acepta la conexión entrante
    client_socket, client_address = server_socket.accept()

    print(f"Conexión aceptada desde {client_address}")

    # Recibe datos del cliente
    data = client_socket.recv(1024)
    print(f"Datos recibidos: {data.decode()}")

    recorrido = perfilar_consulta(data.decode())

    print(recorrido)

    firebase_response = guardar_recorrido(recorrido)
    print(firebase_response)
    dor, dist = predecir_probabilidades_fatiga_distraccion(recorrido)

    response_data = {"message": "Recorrido recibido, se envian las probabilidades de dormirse o distraerse.", "dor": int(dor*100), "dist": int(dist*100)}

    # Convierte el diccionario a una cadena JSON
    response_json = json.dumps(response_data)

    # Envía la respuesta al cliente
    client_socket.send(response_json.encode())

    # Cierra el socket del cliente
    client_socket.close()

    now = datetime.now()
    if now.day == 1:
        if now.hour == 3:
            actualizar_modelo()
    

    time.sleep(1)