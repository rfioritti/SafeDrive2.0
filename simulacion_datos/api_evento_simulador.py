import csv
import random
from datetime import datetime, timedelta

def sim_eventos(id_recorrido,fecha_inicio,fecha):
    
    # Función para generar coordenadas geográficas de Uruguay
    def generate_uruguay_coordinates():
        # Limitar las coordenadas a Uruguay
        min_latitude = -30.0
        max_latitude = -53.0
        min_longitude = -58.4
        max_longitude = -53.2
        latitude = round(random.uniform(min_latitude, max_latitude), 3)
        longitude = round(random.uniform(min_longitude, max_longitude), 3)
        return latitude, longitude
     
    evento = random.randint(1, 6)
    velocidad = round(random.uniform(1, 10), 3)
    id_evento = str(id_recorrido) + str(fecha)
    id_recorrido_id = id_recorrido
    latitud, longitud = generate_uruguay_coordinates()
    
    evento_generado = [fecha, evento, velocidad, id_evento, id_recorrido_id, latitud, longitud]
    return evento_generado


