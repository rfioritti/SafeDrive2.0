import csv
import random
import numpy as np
import geopandas as gpd
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
import warnings

def sim_eventos(id_recorrido,fecha_inicio,fecha):
   
    # Cargar datos geográficos de los países
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    # Filtrar datos para obtener las fronteras de Uruguay
    uruguay_borders = world[world['name'] == 'Uruguay']
    # Obtener la geometría de Uruguay
    uruguay_geometry = uruguay_borders.geometry.values[0]
    
    def generate_uruguay_coordinates():
        minx, miny, maxx, maxy = uruguay_geometry.bounds
        random_longitude = random.uniform(minx, maxx)
        random_latitude = random.uniform(miny, maxy)
        return random_latitude, random_longitude
    
    evento = random.randint(1, 6)
    velocidad = round(random.uniform(1, 10), 3)
    id_evento = str(id_recorrido) + str(fecha)
    id_recorrido_id = id_recorrido
    latitud, longitud = generate_uruguay_coordinates()
    warnings.simplefilter(action='ignore', category=FutureWarning)   
   
    evento_generado = [fecha, evento, velocidad, id_evento, id_recorrido_id, latitud, longitud]
    return evento_generado

 
def haversine_distance(coord1, coord2):
    # Radio de la Tierra en kilómetros
    R = 6371.0
    # Convertir las coordenadas de grados a radianes
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    # Diferencia de coordenadas
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # Distancia en kilómetros
    distance = R * c
    return distance

