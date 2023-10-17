import csv
import random
from datetime import datetime, timedelta

# Nombre del archivo CSV
archivo_csv = 'datos.csv'

# Encabezados del archivo CSV
encabezados = ['id', 'fecha', 'hora', 'zini', 'zfin', 'velProm', 'velMax', 'tRec', 'AB', 'FB', 'kmRec', 'sints', 'dists', 'dorm']

# Crear el archivo CSV y escribir los encabezados
with open(archivo_csv, 'w', newline='') as archivo:
    escritor_csv = csv.DictWriter(archivo, fieldnames=encabezados)
    escritor_csv.writeheader()

    # Generar 100 ejemplos de datos ficticios
    for i in range(1, 101):
        fecha = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H:%M:%S')
        zini = random.uniform(1, 20)
        zfin = random.uniform(1, 20)
        velProm = random.uniform(30, 100)
        velMax = random.uniform(40, 120)
        while velMax < velProm:
            velMax = random.uniform(40, 120)
        tRec = random.randint(10, 480)
        AB = random.randint(0, 15)
        FB = random.randint(0, 15)
        kmRec = random.uniform(0, 800)
        sints = random.randint(0, 10)
        dists = random.randint(0, 1)
        dorm = random.randint(0, 1)

        # Escribir los datos en el archivo CSV
        escritor_csv.writerow({
            'id': i,
            'fecha': fecha,
            'hora': hora,
            'zini': zini,
            'zfin': zfin,
            'velProm': velProm,
            'velMax': velMax,
            'tRec': tRec,
            'AB': AB,
            'FB': FB,
            'kmRec': kmRec,
            'sints': sints,
            'dists': dists,
            'dorm': dorm
        })

print(f'Se han generado y guardado 100 ejemplos en el archivo CSV: {archivo_csv}')
