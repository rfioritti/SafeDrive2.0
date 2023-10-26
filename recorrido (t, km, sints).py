import random
import pandas as pd
from datetime import datetime, timedelta

def random_datetime(start_date, end_date):
    return start_date + timedelta(seconds=random.randint(0, (end_date - start_date).total_seconds()))

data = []

start_date = datetime(2022, 10, 14, 0, 0, 1)
end_date = datetime(2023, 10, 15, 23, 59, 59)

# si al dividir las distracciones entre el timpo del recorrido es menor al valor_distraccion entonces el dato va a ser un bulean 1 
valor_distraccion = 0.05

for i in range(100):
    fecha_inicio = random_datetime(start_date, end_date)
    tiempo_recorrido = random.uniform(10, 250)
    segundos_a_sumar = round(tiempo_recorrido) * 60
    delta = timedelta(seconds=segundos_a_sumar)
    fecha_fin = fecha_inicio + delta
    id_recorrido = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') + 'TEST 123'
    velocidad_promedio = round(random.uniform(20, 55), 4)
    velocidad_maxima = round(random.uniform(30, 110), 4)
    sintomas = random.randint(0, 5)
    frenadas_bruscas = random.randint(0, 5)
    aceleraciones_bruscas = random.randint(0, 5)
    km_recorridos = round(tiempo_recorrido) / 60 * velocidad_promedio
    matricula_id = 'TEST 123'
    distracciones_del_Recorrido = None
    dormidas_recorrido = None

    #prob_dormido = random.uniform(0, 1)
    #prob_distraccion = random.uniform(0, 1)

    indice_distraccion = (tiempo_recorrido*0.19) + (km_recorridos*0.11) + (sintomas*18)

    if indice_distraccion > 110 and random.random() <= 0.90:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    elif 80 <= indice_distraccion <= 110 and random.random() <= 0.60:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    elif 40 <= indice_distraccion < 80 and random.random() <= 0.30:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion
    elif indice_distraccion < 40 and random.random() <= 0.10:
        distracciones_del_Recorrido = tiempo_recorrido*valor_distraccion

    indice_dormido = (tiempo_recorrido*0.38) + (km_recorridos*0.23) + (sintomas*22.50)

    if indice_dormido > 200 and random.random() <= 0.90:
        dormidas_recorrido = 1
    elif 180 <= indice_dormido <= 200 and random.random() <= 0.60:
        dormidas_recorrido = 1
    elif 100 <= indice_dormido < 180 and random.random() <= 0.30:
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

print(data)

# Crear un DataFrame de pandas y guardar en un archivo csv
df = pd.DataFrame(data)
csv_file = 'datos_simulados.csv'
df.to_csv(csv_file, index=False)

print(f'Los datos han sido guardados en {csv_file}.')
