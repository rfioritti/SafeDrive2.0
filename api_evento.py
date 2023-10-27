import csv
import random
from datetime import datetime, timedelta

# Cantidad de filas de datos simulados
num_rows = 100  # Cambia esto al número de filas que desees

# Función para generar una fecha y hora aleatoria
def generate_random_datetime(start_date, end_date):
    time_delta = end_date - start_date
    random_seconds = random.randint(0, int(time_delta.total_seconds()))
    random_date = start_date + timedelta(seconds=random_seconds)
    return random_date

# Función para generar coordenadas geográficas de Uruguay
def generate_uruguay_coordinates():
    # Limitar las coordenadas a Uruguay
    min_latitude = -30.0
    max_latitude = -53.0
    min_longitude = -58.4
    max_longitude = -53.2
    latitude = round(random.uniform(min_latitude, max_latitude), 8)
    longitude = round(random.uniform(min_longitude, max_longitude), 8)
    return latitude, longitude

# Encabezados de las columnas
header = ["fecha_hora", "evento", "velocidad", "id_evento", "id_recorrido_id", "latitud", "longitud"]

# Abre un archivo CSV para escribir
with open("datos_simulados.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)

    # Fechas de inicio y fin
    start_date = datetime(2022, 2, 1, 0, 0, 0)
    end_date = datetime(2022, 2, 28, 23, 59, 59)

    for i in range(num_rows):
        # Genera datos simulados
        fecha_hora = generate_random_datetime(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")
        evento = random.randint(1, 10)
        velocidad = round(random.uniform(1, 10), 3)
        id_evento = generate_random_datetime(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S") + "TEST 123"
        id_recorrido_id = id_evento
        latitud, longitud = generate_uruguay_coordinates()

        # Escribe la fila en el archivo CSV
        row = [fecha_hora, evento, velocidad, id_evento, id_recorrido_id, latitud, longitud]
        writer.writerow(row)

print("Datos simulados generados y guardados en datos_simulados.csv")
