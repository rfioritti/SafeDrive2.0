import random
import pandas as pd
from datetime import datetime, timedelta
from api_evento_simulador import sim_eventos

def random_datetime(start_date, end_date):
    return start_date + timedelta(seconds=random.randint(0, (end_date - start_date).total_seconds()))

data = []
data2 = []
start_date = datetime(2022, 10, 14, 0, 0, 1)
end_date = datetime(2023, 10, 15, 23, 59, 59)

# si al dividir las distracciones entre el timpo del recorrido es menor al valor_distraccion entonces el dato va a ser un bulean 1 
valor_distraccion = 0.05
ejemplos_matriculas = ["ABC 1547","SOL 4544", "PIN 7894", "DEF 4411"]

for i in range(100):
    fecha_inicio = random_datetime(start_date, end_date)
    tiempo_recorrido = random.uniform(10, 400)
    segundos_a_sumar = round(tiempo_recorrido) * 60
    delta = timedelta(seconds=segundos_a_sumar)
    fecha_fin = fecha_inicio + delta
    matricula_seleccionada = random.randint(0, 3)
    id_recorrido = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S') + ejemplos_matriculas[matricula_seleccionada]
    velocidad_promedio = round(random.uniform(20, 55), 4)
    velocidad_maxima = round(random.uniform(30, 110), 4)
    sintomas = random.randint(0, 5)
    frenadas_bruscas = random.randint(0, 5)
    aceleraciones_bruscas = random.randint(0, 5)
    km_recorridos = round(tiempo_recorrido) / 60 * velocidad_promedio
    matricula_id = ejemplos_matriculas[matricula_seleccionada]
    distracciones_del_Recorrido = None
    dormidas_recorrido = None

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

    eventos_del_recorrido = []
    cant_eventos = round((tiempo_recorrido * 60) / 5)
    for x in range(cant_eventos):
        segs = x * 5  # segundos en el que sucede el evento
        fecha = fecha_inicio + timedelta(seconds=segs)
        eventos_del_recorrido = (sim_eventos(id_recorrido, fecha_inicio, fecha))

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


# Crear un DataFrame de pandas y guardar en un archivo csv
df = pd.DataFrame(data)
csv_file = 'recorridos_simulados3.csv'
df.to_csv(csv_file, index=False)

df1 = pd.DataFrame(data2)
csv_file = 'eventos_simulados3.csv'
df1.to_csv(csv_file, index=False)

print(f'Los datos han sido guardados en {csv_file}.')
