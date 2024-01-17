from geopy.distance import geodesic
from shapely.geometry import Point
from decimal import Decimal
import math
import geopandas as gpd
import firebase_admin 
from firebase_admin import credentials, firestore

import csv
import json


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
        
    '''
    print("++++++++++++++++++++++++++++++++++++")
    for i in distancias:
        print (i["distancia"])
    print("++++++++++++++++++++++++++++++++++++")
    '''
    return distancias

# crea una lista de coordenadas alrededor de un punto que no superan el parametro estipulado
# accidentes_dep debe ser un diccionario
# retorna una diccionario
def crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes_dep):

    lista_accidentes = calcular_distancias(accidentes_dep,punto_alpha)
    lista_accidentes = sorted(lista_accidentes, key=lambda x: x["distancia"])# ordeno de menor a mayor
    '''
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    for i in lista_accidentes:
        print (i["distancia"])
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    '''
    aux = [] #variable uitilizada en for
    # quedarme solo con los valores que si dist sea < radio perimietro
    for data in lista_accidentes:
        if data['distancia'] <= radio_perimetro:
            aux.append(data)
        else:
            break
    diccionario = {i: elemento for i, elemento in enumerate(aux)}
    lista_accidentes = diccionario

    '''
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    for id,i in lista_accidentes.items():
        print (str(i["distancia"])+ " //// "+str(i["gravedad"]))
    print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
    '''
    return lista_accidentes

# crea una lista de los puntos con gravedad = 1 osea alta
def encontrar_puntos_riesgo(perimetro):
    lista_puntos_riesgo = []
    for key,i in perimetro.items():
        if i['gravedad'] == 1:
            lista_puntos_riesgo.append(i)
    return lista_puntos_riesgo

def obtener_nivel_riesgo(ruta,db):  # sustituir ruta cuando pasar al servidor '/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson'
    departamentos = gpd.read_file(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson') #FUENTE: https://github.com/alotropico/uruguay.geo
    dep = 0
    dep_prev = -12

    accidentes = "" #guardo la consulta de la BD del los accidedntes del departamento actual
    lista_accidentes = [] # lista de accidentes a un radio del punto alpha
    riesgo = 0
    lista_puntos_mas_accidentes = []
    lista_puntos_riesgo = []
    cant_coord_ruta = len(ruta)

    punto_alpha = -1
    radio_perimetro = 2000 # radio en metros al cual se va aplicar el primetro de busqueda alrededor de un punto_alpha (cada ves que se actualice alpha se hace una busqueda completa)
    radio_busqueda_punto = 25 # radio en metros alrededor de un punto en el cual se buscan accidentes
    actualizacion_alpha = radio_perimetro - radio_busqueda_punto # medidia en metros utilizada para actualizar alpha, si la dist de alpha al siguiente punto es mayor a actualizacion alpha, entonces se acutualiza punto_alpha
    
    
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
            print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* cambie de departamento *-*-*-*-*-*-*-*-*-*-**-*-*-*-*-*-*-*-*")
            dep_prev = dep
            print("departamento: "+str(dep))   

            # no borrar es la coneccion a bd
            '''
            accidentes = db.collection("accidentes").where("departamento", "==", int(dep)).stream() #consulta a la base de datos pqara obtener todos los accidente del departamento
            
            accidentes_dict = {documento.id: documento.to_dict() for documento in accidentes} # paso la consulta a diccionario
            accidentes = accidentes_dict # guardo el diccionario en accidentes
            '''
            # no borrar es la coneccion a bd

            nombre_archivo = "hay_que_borrarlo_depues.csv"
            '''
            # Escribir el diccionario en un archivo CSV
            with open(nombre_archivo, mode='w', newline='') as archivo_csv:
                escritor = csv.DictWriter(archivo_csv, fieldnames=accidentes_dict[list(accidentes_dict.keys())[0]].keys())
                escritor.writeheader()
                escritor.writerows(accidentes_dict.values())
            '''

            # Leer el archivo CSV en una lista de diccionarios
            
            with open(nombre_archivo, mode='r') as archivo_csv:
                lector = csv.DictReader(archivo_csv)
                accidentes = list(lector)

            # Convertir las cadenas JSON en diccionarios
            for accidente in accidentes:
                for key, value in accidente.items():
                    accidente[key] = json.loads(value)
            auxiliar = accidentes
            accidentes = {}
            mi_cont = 0
            for ggg in auxiliar:
                accidentes[mi_cont] = ggg
                mi_cont += 1
            
            '''
            print(accidentes)
            print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            for id,mi_coord in accidentes.items():
                print(str(mi_coord['latitud'])+"   "+str(mi_coord['longitud'])+"   "+str(mi_coord['departamento'])+"   "+str(mi_coord['gravedad']))
            print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
            '''


            
            punto_alpha = {'latitud':coord['latitud'],'longitud': coord['longitud']}

            lista_accidentes = crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes)

            
        else: # dist punto alpha a punto > actualizacion_alpha
            distancia_entre_puntos_km = geodesic((punto_alpha['latitud'],punto_alpha['longitud']), (coord['latitud'], coord['longitud'])).kilometers # calculo la dist entre alpha y el punto actual
            distancia_entre_puntos_metros = round(distancia_entre_puntos_km * 1000) #paso esa distancia en metros
            if dep != 20 and distancia_entre_puntos_metros > actualizacion_alpha:
                punto_alpha = coord
                lista_accidentes = crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes)



            
        
        # listo todos los puntos que estan <= 25 metros de la coord actual
        mi_perimietro = crear_perimetro_busqueda(coord,radio_busqueda_punto,lista_accidentes)
        cant_accidentes = len(mi_perimietro)
        
        riesgo = riesgo + cant_accidentes

        puntos_riesgosos = encontrar_puntos_riesgo(mi_perimietro)
        for i in puntos_riesgosos:
            lista_puntos_riesgo.append(i)
        
        #print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        #print("cant accidentes --->  "+str(cant_accidentes))
        if len(lista_puntos_mas_accidentes) < 3:
            lista_puntos_mas_accidentes.append({"coordenada":coord, "accidentes":cant_accidentes})
        else:
            lista_puntos_mas_accidentes.append({"coordenada":coord, "accidentes":cant_accidentes})
            #print("agregue nuevo elemento   ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[3]["accidentes"]))
            lista_puntos_mas_accidentes = sorted(lista_puntos_mas_accidentes, key=lambda x: x["accidentes"], reverse=True)  # ordeno de mayor a menor
            #print("re ordeno   ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"]))
            lista_puntos_mas_accidentes.pop()
            #print("elimino el ultimo elemento  ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"]))
            #print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        
        #print(str(lista_puntos_mas_accidentes["coorenada"])+" ------> "+str(lista_puntos_mas_accidentes["accidentes"]))

    riesgo_total_ruta = riesgo/cant_coord_ruta
    retornar = [riesgo_total_ruta,lista_puntos_mas_accidentes,lista_puntos_riesgo]
    return retornar

    print("---------------- puntos peligrosos ----------------------")
    print(lista_puntos_riesgo)
    print("---------------- riesgo de la ruta ----------------------")
    print(riesgo/cant_coord_ruta)
    print("---------------- lista de 3 puntos con mas accidentes ----------------------")
    print(lista_puntos_mas_accidentes)
        




'''

# Ejemplo de uso con el JSON de las primeras 40 coordenadas
json_coordenadas = {
  "Marcador1": {"latitud": "-34.90021805742509", "longitud": "-56.19106473959258"},
  "Marcador2": {"latitud": "-34.90017780767356", "longitud": "-56.1905192927954"},
  "Marcador3": {"latitud": "-34.9001388370245", "longitud": "-56.18997370520104"},
  "Marcador4": {"latitud": "-34.90009757073877", "longitud": "-56.18942837564873"},
  "Marcador5": {"latitud": "-34.9000541566938", "longitud": "-56.188883287576665"},
  "Marcador6": {"latitud": "-34.90000840723266", "longitud": "-56.18833849734067"},
  "Marcador7": {"latitud": "-34.89997582673805", "longitud": "-56.18779235834615"},
  "Marcador8": {"latitud": "-34.89994", "longitud": "-56.18728"},
  "Marcador9": {"latitud": "-34.899774793404625", "longitud": "-56.18673712800143"},
  "Marcador10": {"latitud": "-34.89961576913017", "longitud": "-56.18622495313628"},
  "Marcador11": {"latitud": "-34.89945550798324", "longitud": "-56.18571335103631"},
  "Marcador12": {"latitud": "-34.89929767277482", "longitud": "-56.18520063273591"},
  "Marcador13": {"latitud": "-34.89914052649996", "longitud": "-56.18468759813787"},
  "Marcador14": {"latitud": "-34.89898392413501", "longitud": "-56.18417431763828"},
  "Marcador15": {"latitud": "-34.8988276616838", "longitud": "-56.183660883824146"},
  "Marcador16": {"latitud": "-34.89866061077662", "longitud": "-56.18315285732085"},
  "Marcador17": {"latitud": "-34.89847558232169", "longitud": "-56.18265384105515"},
  "Marcador18": {"latitud": "-34.898288565561224", "longitud": "-56.18215593392347"},
  "Marcador19": {"latitud": "-34.89810017509755", "longitud": "-56.18165879345903"},
  "Marcador20": {"latitud": "-34.897915803690346", "longitud": "-56.18115943901206"},
  "Marcador21": {"latitud": "-34.89772384200727", "longitud": "-56.18066471352194"},
  "Marcador22": {"latitud": "-34.89753372346864", "longitud": "-56.180168906152"},
  "Marcador23": {"latitud": "-34.897331164472384", "longitud": "-56.1796813803624"},
  "Marcador24": {"latitud": "-34.897072227303234", "longitud": "-56.179234351220614"},
  "Marcador25": {"latitud": "-34.89675929252206", "longitud": "-56.17884222173526"},
  "Marcador26": {"latitud": "-34.89644079848861", "longitud": "-56.17845803801445"},
  "Marcador27": {"latitud": "-34.896154080843175", "longitud": "-56.17803704736525"},
  "Marcador28": {"latitud": "-34.896249562515095", "longitud": "-56.17733196142084"},
  "Marcador29": {"latitud": "-34.896524241693264", "longitud": "-56.17689868860539"},
  "Marcador30": {"latitud": "-34.89654879517488", "longitud": "-56.17623594130061"},
  "Marcador31": {"latitud": "-34.89650066165473", "longitud": "-56.175691483039"},
  "Marcador32": {"latitud": "-34.89645647494468", "longitud": "-56.17514651114583"},
  "Marcador33": {"latitud": "-34.896413604903906", "longitud": "-56.174601386809485"},
  "Marcador34": {"latitud": "-34.89637270396016", "longitud": "-56.174056034310965"},
  "Marcador35": {"latitud": "-34.896331405884126", "longitud": "-56.173510727432046"},
  "Marcador36": {"latitud": "-34.89628853105142", "longitud": "-56.17296560090792"},
  "Marcador37": {"latitud": "-34.896244455748764", "longitud": "-56.17242061851542"},
  "Marcador38": {"latitud": "-34.896199466106495", "longitud": "-56.17187574598909"},
  "Marcador39": {"latitud": "-34.89615735674153", "longitud": "-56.17133054036547"},
  "Marcador40": {"latitud": "-34.8961168039742", "longitud": "-56.170785151043084"}
}

# Configura las credenciales del servicio de Firebase
                            # cambiar
cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
firebase_admin.initialize_app(cred)

# Obtiene una referencia a la base de datos Firestore
db = firestore.client()

coordenada_fija = (-34.891525, -56.187188)
#resultado_distancias = calcular_distancias(json_coordenadas,coordenada_fija)

obtener_nivel_riesgo(json_coordenadas,db)
'''