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

def eliminar_elementos_por_distancia(lista_diccionarios,radio_perimetro):
    # Crear una nueva lista sin los elementos no deseados
    # Crear una nueva lista con diccionarios cuya distancia es menor o igual a 4000
    nueva_lista = []
    for diccionario in lista_diccionarios:
        distancia = diccionario.get('distancia', 1000000000)
        if distancia <= radio_perimetro+2000:
            nueva_lista.append(diccionario)


    return nueva_lista

def crear_perimetro_busqueda_punto(punto_alpha,radio_perimetro,accidentes_dep2,centro):
    accidentes_dep = accidentes_dep2.copy()
    
    # reduzco los puntos a analisar a partir de su distancia en comparacion con el centro del perimetro de busqueda y el pto a evaluar 
    dist_alpha_centro = geodesic((punto_alpha['latitud'],punto_alpha['longitud']), (centro['latitud'], centro['longitud'])).meters
    tope = dist_alpha_centro + radio_perimetro+1
    piso = dist_alpha_centro - radio_perimetro-1
    aux = 0
    aux_dic = {}
    for id,coord in accidentes_dep.items():
        if coord['distancia']>tope:
            break
        if coord['distancia']>=piso:
            aux_dic[aux] = coord
            aux = aux + 1
    
    accidentes_dep = aux_dic



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

    return lista_accidentes

def convertir_bd_a_dict(data):
    aux = {}

    cont = 0
    for clave,fila in data.items(): 
        elementos_cadena = fila['cadena']
        for fila_iterada in elementos_cadena:
            aux[cont] = fila_iterada
            cont +=1
    return aux

def crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes):

    #solo sirve para el print
    cant_accidentes_dep = 0
    for mi_clave,mi_fila in accidentes.items():
        cant_accidentes_dep = cant_accidentes_dep + len(mi_fila['cadena'])

    print("comenzo a ordenar perimetro +++++++++++++++++++++++++++++++++++++++++ ENTRADAS EN bd " + str(len(accidentes))+" CANTIDAD DE ACCIDENTES: " + str(cant_accidentes_dep ))
    accidentes_dep = accidentes.copy()
    # armo una lista con todos los centros del departamento actual
    seleccion = {}
    for llave,fila in accidentes_dep.items():
        seleccion[llave] = fila['centro']

    #calculo la distancia a todos los centro en comparacion del punto alpha
    seleccion_aux = calcular_distancias(seleccion,punto_alpha)

    # creo una lista con los centros a menos de radio_perimetro + 2000m del punto alpha
    seleccion_aux = eliminar_elementos_por_distancia(seleccion_aux,radio_perimetro)

    # elimino todos los elementos que estan fuera del perimetro reducido // en este caso filtramos y solo nos quedamos con los centros que estan amenos de radio_perimetro + 2000m de punto_alpha
    elimino_llave = []
    for llave,fila in accidentes_dep.items():
        eliminar = True
        coord = fila['centro'] 
        for i in seleccion_aux:
            if coord['latitud'] == i['latitud'] and coord['longitud'] == i['longitud']:
                eliminar = False
                break
        if eliminar == True:
            elimino_llave.append(llave) 
    for ii in elimino_llave:
        del accidentes_dep[ii]
        
    print("entradas reducias -> "+str(len(accidentes_dep)))
    
    # convierto a accidentes en un diccionarios de diccionarios para que sea compatibe con las funciones que trabajo (ago un diccionario que tiene todas las cordenadas en formato diccionario)
    accidentes_dep = convertir_bd_a_dict(accidentes_dep)
    print("cantidad de accidentes a evaluar --> "+str(len(accidentes_dep)))

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
    print("perimetro reducido = "+str(len(lista_accidentes)))
    print("termino de ordenar perimetro +++++++++++++++++++++++++++++++++++++++++++ ")
    return lista_accidentes

# crea una lista de los puntos con gravedad = 1 osea alta
def encontrar_puntos_riesgo(perimetro):
    lista_puntos_riesgo = []
    for key,i in perimetro.items():
        if i['gravedad'] == 1:
            lista_puntos_riesgo.append(i)
    return lista_puntos_riesgo



def obtener_nivel_riesgo(ruta,db):  # sustituir ruta cuando pasar al servidor /home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson
    departamentos = gpd.read_file(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson') #FUENTE: https://github.com/alotropico/uruguay.geo
    dep = 0
    dep_prev = -12

    accidentes = "" #guardo la consulta de la BD del los accidedntes del departamento actual
    lista_accidentes = [] # lista de accidentes a un radio del punto alpha
    riesgo = 0
    lista_puntos_mas_accidentes = []
    lista_puntos_riesgo = []
    cant_coord_ruta = len(ruta)

    cant_foco_accidentes = int((cant_coord_ruta*50)/20000) #calculo la cantidad de elementos que va a tener el top de mas accidentes de la ruta segun la distancia de la misma
    if cant_foco_accidentes < 3:
        cant_foco_accidentes = 3


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

            # coneccion a bd
            accidentes = db.collection("accidentes").where("departamento", "==", int(dep)).stream() #consulta a la base de datos pqara obtener todos los accidente del departamento
            
            accidentes_dict = {documento.id: documento.to_dict() for documento in accidentes} # paso la consulta a diccionario
            accidentes = accidentes_dict # guardo el diccionario en accidentes


            
            punto_alpha = {'latitud':coord['latitud'],'longitud': coord['longitud']}
            
            lista_accidentes = crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes)

            
        else: # dist punto alpha a punto > actualizacion_alpha
            distancia_entre_puntos_km = geodesic((punto_alpha['latitud'],punto_alpha['longitud']), (coord['latitud'], coord['longitud'])).kilometers # calculo la dist entre alpha y el punto actual
            distancia_entre_puntos_metros = round(distancia_entre_puntos_km * 1000) #paso esa distancia en metros
            if dep != 20 and distancia_entre_puntos_metros > actualizacion_alpha:
                punto_alpha = coord
                print("alpha fue actualizado ..........departamento "+str(dep)+"...........nuevo perimetro de busqueda")
                lista_accidentes = crear_perimetro_busqueda(punto_alpha,radio_perimetro,accidentes)



            
        
        # listo todos los puntos que estan <= 25 metros de la coord actual
        mi_perimietro = crear_perimetro_busqueda_punto(coord,radio_busqueda_punto,lista_accidentes,punto_alpha)
        cant_accidentes = len(mi_perimietro)

        puntos_riesgosos = encontrar_puntos_riesgo(mi_perimietro)
        for i in puntos_riesgosos:
            lista_puntos_riesgo.append(i)
        
        #print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        print("coord lat lon "+str(coord['latitud'])+","+str(coord['longitud'])+" cant accidentes --->  "+str(cant_accidentes)+" departamento actual "+str(dep))
        if len(lista_puntos_mas_accidentes) < cant_foco_accidentes:
            lista_puntos_mas_accidentes.append({"coordenada":coord, "accidentes":cant_accidentes})
        else:
            lista_puntos_mas_accidentes.append({"coordenada":coord, "accidentes":cant_accidentes})
            #print("agregue nuevo elemento   ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[3]["accidentes"]))
            lista_puntos_mas_accidentes = sorted(lista_puntos_mas_accidentes, key=lambda x: x["accidentes"], reverse=True)  # ordeno de mayor a menor
            #print("re ordeno   ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"]))
            lista_puntos_mas_accidentes.pop()
           # print("elimino el ultimo elemento  ====> "+str(lista_puntos_mas_accidentes[0]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[1]["accidentes"])+" ====== "+str(lista_puntos_mas_accidentes[2]["accidentes"]))
           # print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
        
        #print(str(lista_puntos_mas_accidentes["coorenada"])+" ------> "+str(lista_puntos_mas_accidentes["accidentes"]))
   
    # calculo cual es la cocentracion de accidentes que posee
    suma_top_concetracion_accidentes = 0
    for i in lista_puntos_mas_accidentes:
        suma_top_concetracion_accidentes = suma_top_concetracion_accidentes + i["accidentes"]
    
    #obtengo los promedios desde la colleccion historial de la BD
    historial_ref = firestore.client().collection('historial').document("1")
    doc_snapshot = historial_ref.get()
    promedios = doc_snapshot.to_dict()

    #inicializo variables con los promedios
    promedio_accidentes_graves = promedios["promedio_accidentes_graves"]
    promedio_concentracion_accidentes = promedios["promedio_concentracion_accidentes"]
    total_elementos = promedios["total_elementos"]

    #calculo los nuevos promedios
    promedio_accidentes_graves = (promedio_accidentes_graves * total_elementos + len(lista_puntos_riesgo))/(total_elementos+1)
    promedio_concentracion_accidentes = (promedio_concentracion_accidentes * total_elementos + suma_top_concetracion_accidentes)/(total_elementos+1)
   
    # calculo el riesgo con la ponderacion elegida
    riesgo_total_ruta = ((suma_top_concetracion_accidentes/(promedio_concentracion_accidentes*2))*7)+((len(lista_puntos_riesgo)/(promedio_accidentes_graves*2))*3)

   

    historia = {
        'promedio_concentracion_accidentes': promedio_concentracion_accidentes,
        'promedio_accidentes_graves': promedio_accidentes_graves,
        'total_elementos': total_elementos + 1 
    }

    # Guarda el diccionario como documento en la colección 'accidentes'
    historial_ref.set(historia)

    retornar = [riesgo_total_ruta,lista_puntos_mas_accidentes,lista_puntos_riesgo]
    print("---------------- puntos peligrosos ----------------------")
    print(lista_puntos_riesgo)
    print("---------------- riesgo de la ruta ----------------------")
    print(riesgo_total_ruta)
    print("---------------- lista de 3 puntos con mas accidentes ----------------------")
    print(lista_puntos_mas_accidentes)
    return retornar
