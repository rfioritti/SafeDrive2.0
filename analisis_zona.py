from geopy.distance import geodesic
from shapely.geometry import Point
from decimal import Decimal
import math
import geopandas as gpd
import firebase_admin 
from firebase_admin import credentials, firestore
import sys
import time
import csv
import json
csv.field_size_limit(2**31-1)

# obtiene las distancia en metors de un json de coordenadas con un punto fijo
def calcular_distancias(coordenadas, coordenada_fija):
    #print("entro a la function")
    # Coordenada fija
    # coordenada_fija = (-34.891525, -56.187188)

    # Calcular la distancia para cada coordenada en el diccionario
    distancias = []
    i = 0
    for id,coord in coordenadas.items():
        
        latitud = coord['latitud']
        longitud = coord['longitud']
        gravedad = coord['gravedad']
        distancia_km = geodesic((coordenada_fija['latitud'],coordenada_fija['longitud']), (latitud, longitud)).kilometers
        distancia_metros = round(distancia_km * 1000)  # Convert to meters
        distancias.append({"distancia": distancia_metros, "latitud": latitud, "longitud": longitud, "gravedad": gravedad})
        

    return distancias

# crea una lista de coordenadas alrededor de un punto que no superan el parametro estipulado
# accidentes_dep debe ser un diccionario
# retorna una diccionario

def eliminar_elementos_por_distancia(lista_diccionarios):
    # Crear una nueva lista sin los elementos no deseados
    # Crear una nueva lista con diccionarios cuya distancia es menor o igual a 4000
    nueva_lista = []
    for diccionario in lista_diccionarios:
        distancia = diccionario.get('distancia', 1000000000)
        if distancia <= 2200:
            nueva_lista.append(diccionario)


    return nueva_lista

# extraigo coordenadas almacenadas en 'cadena' y las combierto en formato dic
def convertir_bd_a_dict(data):
    aux = {}

    cont = 0
    for clave,fila in data.items(): 
        elementos_cadena = fila['cadena']
        for fila_iterada in elementos_cadena:
            aux[cont] = fila_iterada
            cont +=1
    return aux

def crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes_dep):
    #print("comenzo a ordenar perimetro ++++++++++++++++++++++++++++++++++++++++++++++++++" + str(len(accidentes_dep)))

    # armo una lista con todos los centros del departamento actual
    seleccion = {}
    for llave,fila in accidentes_dep.items():
        seleccion[llave] = fila['centro']

    #calculo la distancia a todos los centro en comparacion del punto alpha
    seleccion_aux = calcular_distancias(seleccion,punto_alpha)

    # creo una lista con los centros a menos de 2200m del punto alpha
    seleccion_aux = eliminar_elementos_por_distancia(seleccion_aux)

    # elimino todos los elementos que estan fuera del perimetro reducido // en este caso filtramos y solo nos quedamos con los centros que estan amenos de 2200m de punto_alpha
    elimino_llave = []
    accidentes_dep_aux = {}
    for llave,fila in accidentes_dep.items():
        contrdorId = 0
        eliminar = True
        coord = fila['centro'] 
        for i in seleccion_aux:
            if coord['latitud'] == i['latitud'] and coord['longitud'] == i['longitud']:
               dic_aux= {}
               dic_aux[1] = fila
               cadena = convertir_bd_a_dict(dic_aux)
               disti_centro = i['distancia']
               suelo = disti_centro-radio_perimetro-1
               techo = disti_centro+radio_perimetro+1
               
               for mi_id,mi_valor in cadena.items():
                   if mi_valor['distancia']>suelo and mi_valor['distancia']<techo: 
                       accidentes_dep_aux[contrdorId]=mi_valor
                       contrdorId = contrdorId + 1
               break 
    
    accidentes_dep = accidentes_dep_aux  

    lista_accidentes = calcular_distancias(accidentes_dep,punto_alpha)
    lista_accidentes = sorted(lista_accidentes, key=lambda x: x["distancia"])# ordeno de menor a mayor
    
    aux = [] #variable uitilizada en for
    # quedarme solo con los valores que si dist sea < radio perimietro
    for data in lista_accidentes:
        if data['distancia'] <= radio_perimetro:
            aux.append(data)
        else:
            break
    diccionario = {i: elemento for i, elemento in enumerate(aux)}
    lista_accidentes = diccionario
    return [lista_accidentes,seleccion]


def guardar_diccionario_en_csv(diccionario, nombre_archivo):
   
    with open(nombre_archivo, 'w', newline='') as csvfile:
        fieldnames = ['clave', 'departamento', 'cadena', 'centro']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for clave, valor in diccionario.items():
            writer.writerow({'clave': clave, 'departamento': valor['departamento'],
                             'cadena': json.dumps(valor['cadena']), 'centro': json.dumps(valor['centro'])})

def cargar_csv_a_diccionario(nombre_archivo):
   
    diccionario = {}
    with open(nombre_archivo, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            clave = row['clave']
            departamento = int(row['departamento'])
            cadena = json.loads(row['cadena'])
            centro = json.loads(row['centro'])
            diccionario[clave] = {'departamento': departamento, 'cadena': cadena, 'centro': centro}

    return diccionario

def obtener_nivel_riesgo(ruta,accidentes_dep_rpi,zona_reducida,punto_alpha,db):  # sustituir ruta cuando pasar al servidor  /home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson
    inicio = time.time()
    departamentos = gpd.read_file(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson') #FUENTE: https://github.com/alotropico/uruguay.geo
    dep = 0
    if len(accidentes_dep_rpi) == 0:
        dep_prev = -12
    else:
        dep_prev = next(iter(accidentes_dep_rpi.items()))
        point = Point(dep_prev['longitud'], dep_prev['latitud'])  # Crea un objeto Point con las coordenadas
        departamento = departamentos[departamentos.contains(point)]['NAME_1']  # busca el punto dentro del dataset de geopandas
        if not departamento.empty:
            dep_prev = departamento.values[0]
        else:
            dep_prev = 20
    

    accidentes = accidentes_dep_rpi #guardo la consulta de la BD del los accidedntes del departamento actual
    lista_accidentes = [] # lista de accidentes a un radio del punto alpha
    punto_alpha = -1
    radio_perimetro = 200 # radio en metros al cual se va aplicar el primetro de busqueda alrededor de un punto_alpha (cada ves que se actualice alpha se hace una busqueda completa)
    
    retornar = []
    
    for marcador,coord in ruta.items():

        # identifico en que departamento estan las coordenadas 
        point = Point(coord['longitud'], coord['latitud'])  # Crea un objeto Point con las coordenadas
        departamento = departamentos[departamentos.contains(point)]['NAME_1']  # busca el punto dentro del dataset de geopandas
        if not departamento.empty:
            dep = departamento.values[0]
        else:
            dep = 20
        
        #verifico que la coordenada siga en el mismo dep, sino actualizo los puntos obtenidos
        if dep != dep_prev and dep < 20:
            dep_prev = dep
             
            # coneccion a bd
            accidentes = db.collection("accidentes").where("departamento", "==", int(dep)).stream() #consulta a la base de datos para obtener todos los accidente del departamento
            
            accidentes_dict = {documento.id: documento.to_dict() for documento in accidentes} # paso la consulta a diccionario
            accidentes = accidentes_dict # guardo el diccionario en accidentes
            
            
            accidentes_dep_rpi = accidentes
            punto_alpha = {'latitud':coord['latitud'],'longitud': coord['longitud']}
            lista_accidentes,accidentes_dep_rpi = crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes_dep_rpi)

        
        cant_accidentes = len(lista_accidentes)

        #obtengo los promedios desde la colleccion historial de la BD
        historial_ref = firestore.client().collection('historial').document("2")
        doc_snapshot = historial_ref.get()
        promedios = doc_snapshot.to_dict()
        promedio_accidentes = promedios["promedio_accidentes"]
        total_elementos = promedios["total_elementos"]

        nuevo_prom = ((promedio_accidentes*total_elementos)+cant_accidentes)/(total_elementos+1)

        historia = {
        'promedio_accidentes': nuevo_prom,
        'total_elementos': total_elementos + 1 
        }

        # Guarda el diccionario como documento en la colección 'accidentes'
        historial_ref.set(historia)

        riesgo_zona = (cant_accidentes/(promedio_accidentes*2))*10
        accidentes_dep_rpi ={}
        zona_reducida = {}
        punto_alpha = {}
        retornar = [riesgo_zona,accidentes_dep_rpi,zona_reducida,punto_alpha]
        print(str(cant_accidentes)+"    "+str(riesgo_zona)) 
    fin = time.time()
    print("tiempo en ms: "+str(int((fin-inicio)*1000)))
    return retornar

 