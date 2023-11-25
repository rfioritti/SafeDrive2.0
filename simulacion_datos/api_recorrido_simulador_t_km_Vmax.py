import random
import pandas as pd
from datetime import datetime, timedelta
import warnings
from api_evento_simulador import sim_eventos, haversine_distance

def random_datetime(start_date, end_date):
    return start_date + timedelta(seconds=random.randint(0, (end_date - start_date).total_seconds()))

data = []
data2 = []
start_date = datetime(2022, 10, 14, 0, 0, 1)
end_date = datetime(2023, 10, 15, 23, 59, 59)

# si al dividir las distracciones entre el timpo del recorrido es menor al valor_distraccion entonces el dato va a ser un bulean 1 
valor_distraccion = 0.05
ejemplos_matriculas = ["ABC 1547","SOL 4544", "PIN 7894", "DEF 4411"]
warnings.simplefilter(action='ignore', category=FutureWarning)


for i in range(100):
    fecha_inicio = random_datetime(start_date, end_date)
    matricula_seleccionada = random.randint(0, 3)
    id_recorrido = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') + ejemplos_matriculas[matricula_seleccionada]
    velocidad_maxima = round(random.uniform(30, 110))
    velocidad_promedio = round(random.uniform(20, velocidad_maxima))
    sintomas = random.randint(0, 5)
    frenadas_bruscas = random.randint(0, 6)
    aceleraciones_bruscas = random.randint(0, 5)

    matricula_id = ejemplos_matriculas[matricula_seleccionada]
    distracciones_del_Recorrido = None
    dormidas_recorrido = None

    eventos_del_recorrido = []
    coordenadas_inicio = []
    coordenadas_fin = []

    for x in range(2):
        segs = x * 5  # segundos en el que sucede el evento
        fecha = fecha_inicio + timedelta(seconds=segs)
        eventos_del_recorrido = (sim_eventos(id_recorrido, fecha_inicio, fecha))
        if x == 0:
            lat_inicio = eventos_del_recorrido[5]
            lon_inicio = eventos_del_recorrido[6]
            coordenadas_inicio.append(lat_inicio)
            coordenadas_inicio.append(lon_inicio)        
        if x == 1:
            lat_fin = eventos_del_recorrido[5]
            lon_fin = eventos_del_recorrido[6]
            coordenadas_fin.append(lat_fin)
            coordenadas_fin.append(lon_fin)    

        row2 = {
            'fecha_hora': eventos_del_recorrido[0],
            'evento': eventos_del_recorrido[1],
            'velocidad': eventos_del_recorrido[2],
            'id_evento': eventos_del_recorrido[3],
            'id_recorrido_id': eventos_del_recorrido[4],
            'latitud': eventos_del_recorrido[5],
            'longitud': eventos_del_recorrido[6]
        }
        data2.append(row2)

    km_recorridos = round(haversine_distance(coordenadas_inicio, coordenadas_fin))
    tiempo_recorrido = round((km_recorridos / velocidad_promedio) * 60)
    segundos_a_sumar = round(tiempo_recorrido) * 60
    delta = timedelta(seconds=segundos_a_sumar)
    fecha_fin = fecha_inicio + delta

    indice_distraccion = (tiempo_recorrido*0.19) + (km_recorridos*0.11) + (90/velocidad_maxima)

    if indice_distraccion < 25 and random.random() <= 0.90:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    elif indice_distraccion >= 25 and indice_distraccion <= 30 and random.random() <= 0.60:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    elif indice_distraccion > 30 and random.random() <= 0.30:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    
    indice_dormido = (tiempo_recorrido*0.38) + (km_recorridos*0.23) + (velocidad_maxima*0.8)

    if indice_dormido > 150 and random.random() <= 0.90:
        dormidas_recorrido = 1
    elif 120 <= indice_dormido <= 150 and random.random() <= 0.60:
        dormidas_recorrido = 1
    elif 100 <= indice_dormido < 120 and random.random() <= 0.30:
        dormidas_recorrido = 0
    elif indice_dormido < 100 and random.random() <= 0.10:
        dormidas_recorrido = 0

   
    row = {
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'id_recorrido': id_recorrido,
        'velocidad_promedio': velocidad_promedio,
        'velocidad_maxima': velocidad_maxima,
        'sintomas': sintomas,
        'frenadas_bruscas': frenadas_bruscas,
        'aceleraciones_bruscas': aceleraciones_bruscas,
        'km_recorridos': km_recorridos,
        'tiempo_recorrido': tiempo_recorrido,
        'matricula_id': matricula_id,
        'distracciones': distracciones_del_Recorrido,
        'dormido': dormidas_recorrido
     }

    data.append(row)


# Crear un DataFrame de pandas y guardar en un archivo csv
df = pd.DataFrame(data)
csv_file = 'recorridos_simulados.csv'
df.to_csv(csv_file, index=False)

df1 = pd.DataFrame(data2)
csv_file = 'eventos_simulados.csv'
df1.to_csv(csv_file, index=False)

print(f'Los datos han sido guardados en {csv_file}.')
