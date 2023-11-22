import socket
from procesar_respuesta import perfilar_consulta
from guardadoDatos import guardar_recorrido
from prediccion_fatiga_distraccion import predecir_probabilidades_fatiga_distraccion

# Configura el servidor
server_ip = '0.0.0.0'  # Escucha en todas las interfaces de red
server_port = 2225

# Crea un socket para escuchar conexiones entrantes
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)

print(f"Esperando conexiones en {server_ip}:{server_port}")

# Acepta la conexión entrante
client_socket, client_address = server_socket.accept()

print(f"Conexión aceptada desde {client_address}")

# Recibe datos del cliente
data = client_socket.recv(1024)
print(f"Datos recibidos: {data.decode()}")

recorrido = perfilar_consulta(data.decode())
guardar_recorrido(recorrido)

dor, dist = predecir_probabilidades_fatiga_distraccion(recorrido)

response_data = {"message": "Recorrido recibido, se envian las probabilidades de dormirse o distraerse.", "dor": dor, "dist": dist}

# Convierte el diccionario a una cadena JSON
response_json = json.dumps(response_data)

# Envía la respuesta al cliente
client_socket.send(response_json.encode())

# Cierra el socket del cliente
client_socket.close()