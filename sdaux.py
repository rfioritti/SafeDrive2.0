import socket

# Configura el servidor
server_ip = '0.0.0.0'  # Escucha en todas las interfaces de red
server_port = 8080

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

# Envía una respuesta al cliente
response = "Hola, cliente! Recibí tu mensaje."
client_socket.send(response.encode())

# Cierra el socket del cliente
client_socket.close()