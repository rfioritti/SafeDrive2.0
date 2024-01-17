import csv
import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from pyproj import Proj, transform

from geopy.distance import geodesic
from shapely.geometry import Point
from decimal import Decimal
import math

cred = credentials.Certificate(r"C:\Users\admin\Desktop\tesis\safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def limpiar_dato(dato, es_encabezado=False):
    # Función para limpiar los datos (eliminar espacios extras, etc.)
    # dato_limpio = dato.strip()

    # Eliminar la segunda coma (,) en cada fila (excepto en el encabezado)
    if not es_encabezado:
        partes = dato.split(',')
        if len(partes) > 1:
            dato = partes[0] + ','.join(partes[1:])

    return dato



def fusionar_txt_a_csv(directorio_entrada, archivo_csv_salida):
    # Abre el archivo CSV de salida en modo escritura sin agregar comillas
    with open(archivo_csv_salida, 'w', newline='', encoding='utf-8') as csv_salida:
        escritor_csv = csv.writer(csv_salida, quoting=csv.QUOTE_NONE, escapechar='\\')

        # Itera sobre cada archivo TXT en el directorio
        for archivo_txt in os.listdir(directorio_entrada):
            ruta_completa = os.path.join(directorio_entrada, archivo_txt)

            # Verifica si es un archivo y si tiene la extensión TXT
            if os.path.isfile(ruta_completa) and archivo_txt.lower().endswith('.txt'):
                # Abre el archivo TXT en modo lectura
                with open(ruta_completa, 'r', encoding='utf-8') as txt_entrada:
                    lector_txt = csv.reader(txt_entrada, delimiter=',')  # Ajusta el delimitador según tu caso

                    # Encabezado original
                    encabezado_original = next(lector_txt)

                    # Escribe el encabezado original en el archivo CSV de salida sin comillas
                    escritor_csv.writerow([limpiar_dato(dato, es_encabezado=True) for dato in encabezado_original])

                    # Itera sobre cada fila del archivo TXT
                    for fila in lector_txt:
                        # Limpia cada dato en la fila y elimina la segunda coma (excepto en el encabezado)
                        fila_limpia = [limpiar_dato(dato) for dato in fila]

                        # Escribe la fila limpia en el archivo CSV de salida sin comillas
                        escritor_csv.writerow(fila_limpia)



def conservar_columnas_pandas(directorio_entrada, archivo_csv_entrada, archivo_csv_salida):
    # Lee el archivo CSV de entrada
    df = pd.read_csv(archivo_csv_entrada)

    # Elimina espacios en blanco en los nombres de las columnas
    df.columns = df.columns.str.strip()

    # Limpieza de datos, por ejemplo, eliminar espacios adicionales en las celdas
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Conserva solo las columnas deseadas si existen
    columnas_a_conservar = ['Departamento', 'Gravedad', 'X', 'Y']

    # Verifica si las columnas existen en el DataFrame
    columnas_existen = set(columnas_a_conservar) & set(df.columns)

    if columnas_existen:
        # Filtra el DataFrame para conservar solo las columnas deseadas
        df_filtrado = df[columnas_a_conservar]

        # Convierte las columnas 'X' e 'Y' a tipo float (manejando valores no numéricos)
        df_filtrado['X'] = pd.to_numeric(df_filtrado['X'], errors='coerce')
        df_filtrado['Y'] = pd.to_numeric(df_filtrado['Y'], errors='coerce')

        # Elimina las filas que contienen valores no numéricos en 'X' o 'Y'
        df_filtrado = df_filtrado.dropna(subset=['X', 'Y'])

        # Guarda el DataFrame filtrado en un nuevo archivo CSV
        df_filtrado.to_csv(archivo_csv_salida, index=False)
    else:
        print("Las columnas especificadas no existen en el DataFrame.")




def mapeo():
    # Leer el archivo CSV
    archivo_entrada = 'salida_columnas.csv'
    df = pd.read_csv(archivo_entrada)

    # Mapear los nombres de departamentos a valores enteros
    mapeo_departamentos = {
        'MONTEVIDEO': 1, 'CANELONES': 2, 'MALDONADO': 3, 'ROCHA': 4, 'CERRO LARGO': 5,
        'TREINTA Y TRES': 6, 'RIVERA': 7, 'ARTIGAS': 8, 'SALTO': 9, 'PAYSANDU': 10,
        'RIO NEGRO': 11, 'SORIANO': 12, 'COLONIA': 13, 'SAN JOSE': 14, 'FLORES': 15,
        'FLORIDA': 16, 'DURAZNO': 17, 'LAVALLEJA': 18, 'TACUAREMBO': 19
    }

    mapeo_gravedad = {
        'SIN LESIONADOS': 0, 'LEVE': 0, 'GRAVE': 1, 'FATAL': 1
    }

    # Aplicar el mapeo a la columna correspondiente y convertir a tipo entero
    df['Departamento'] = df['Departamento'].map(mapeo_departamentos)
    df['Gravedad'] = df['Gravedad'].map(mapeo_gravedad)

    # Rellenar valores NaN con algún valor específico (en este caso, 0)
    df['Departamento'] = df['Departamento'].fillna(0).astype(int)
    df['Gravedad'] = df['Gravedad'].fillna(0).astype(int)        

    # Guardar el DataFrame modificado en un nuevo archivo CSV
    archivo_salida = 'salida_columnas_transformado.csv'
    df.to_csv(archivo_salida, index=False)

    print(f'Transformación completa. Resultado guardado en "{archivo_salida}"')



def convertir_utm_a_geograficas(archivo_entrada, archivo_salida):
    # Leer el archivo CSV
    df = pd.read_csv(archivo_entrada)

    # Definir el sistema de coordenadas UTM (wgs84) con la zona UTM y el hemisferio
    utm_zone = 21
    utm_proj = Proj(proj='utm', zone=utm_zone, ellps='WGS84', south=True)  # Especificar el hemisferio sur

    # Convertir las coordenadas UTM a geográficas (latitud, longitud)
    Y, X = transform(utm_proj, proj_latlon, df['X'].values, df['Y'].values)

    # Eliminar las columnas originales 'X' e 'Y'
    df = df.drop(columns=['X', 'Y'])

    # Crear nuevas columnas 'Longitud' y 'Latitud' con las coordenadas geográficas
    df['Longitud'] = Y
    df['Latitud'] = X

    df = df.rename(columns={'Departamento': 'departamento', 'Gravedad': 'gravedad', 'Latitud': 'latitud', 'Longitud': 'longitud'})

    # Reorganizar el orden de las columnas
    df = df[['departamento', 'gravedad', 'latitud', 'longitud']]
    
    # Guardar el DataFrame modificado en un nuevo archivo CSV
    df.to_csv(archivo_salida, index=False)

    print(f'Conversión completa. Resultado guardado en "{archivo_salida}"')




# obtiene las distancia en metors de una lista de diccionarios de coordenadas con un punto fijo
def calcular_distancias(coordenadas, coordenada_fija):
    #print("entro a la function")
    # Coordenada fija
    # coordenada_fija = (-34.891525, -56.187188)

    # Calcular la distancia para cada coordenada en el diccionario
    distancias = []
    #distancias.append(coordenada_fija)
    for id,coord in coordenadas.items():
        latitud = coord['latitud']
        longitud = coord['longitud']
        gravedad = coord['gravedad']
        dep = coord['departamento']
        distancia_km = geodesic((coordenada_fija['latitud'],coordenada_fija['longitud']), (latitud, longitud)).kilometers
        distancia_metros = round(distancia_km * 1000)  # Convert to meters
        if distancia_metros <= 1000 and dep == coordenada_fija['departamento']:
            distancias.append({"departamento":dep, "distancia": distancia_metros, "latitud": latitud, "longitud": longitud, "gravedad": gravedad,"id":id})
        
    '''
    print("++++++++++++++++++++++++++++++++++++")
    for i in distancias:
        print (i["distancia"])
    print("++++++++++++++++++++++++++++++++++++")
    '''
    print("---------------------------------------------------- ")
    print("elementos agrupados ---------> "+ str(len(distancias)))
    print(" ")
    return distancias


'''
# recibe un dic y duevuelve un dic
def reduccion_datos(salida_geograficas):
    print("----------------------------------")
    salida_geograficas['check'] = 0
    mi_diccionario = {}
    id = 0
    for index, row in salida_geograficas.iterrows():
        print("+++++++++++++++++++++++++++++++++++++++")
        agrupacion = calcular_distancias(salida_geograficas.to_dict(orient='index'), row.to_dict())

        # Nuevo elemento que deseas agregar
        nueva_clave = id
        nuevo_centro = (37.0, -122.0)
        nuevo_departamento = 8
        nueva_cadena = agrupacion
        id += 1

        # Agregar el nuevo elemento al diccionario
        mi_diccionario[nueva_clave] = {
            'centro': nuevo_centro,
            'departamento': nuevo_departamento,
            'cadena': nueva_cadena
        }

        print("/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/")
        print(mi_diccionario)
        
'''
# recibe un dic y duevuelve un dic
def reduccion_datos(salida_geograficas):
    mi_diccionario = {}
    id = 0
    aux = salida_geograficas.to_dict(orient='index')
    while aux:
        print("tamano diccionario -------------> "+str(len(aux)))
        print("+++++++++++++++++++++++++++++++++++++++")
        clave_actual = next(iter(aux))
        print(clave_actual)
        fila =  aux[clave_actual]
        agrupacion = calcular_distancias(aux,fila)

        # Nuevo elemento que deseas agregar
        nueva_clave = id
        nuevo_centro = fila
        nuevo_departamento = fila['departamento']
        nueva_cadena = agrupacion
        id += 1

        # Agregar el nuevo elemento al diccionario
        mi_diccionario[nueva_clave] = {
            'centro': nuevo_centro,
            'departamento': nuevo_departamento,
            'cadena': nueva_cadena
        }

        for i in agrupacion:
            #print("se elimino"+str(i['id']))
            del aux[i['id']]
        

    print("cantidad de agrupaciones totales:"+str(id))
    return mi_diccionario

if __name__ == "__main__":
    
    directorio_entrada = r"C:\Users\admin\Desktop\tesis\safedrive_aux\Datos UNASEV"
    archivo_salida_csv = 'salida.csv'

    fusionar_txt_a_csv(directorio_entrada, archivo_salida_csv)

    archivo_csv_entrada = r"C:\Users\admin\Desktop\tesis\safedrive_aux\Datos UNASEV\salida.csv"
    archivo_csv_salida = r'C:\Users\admin\Desktop\tesis\safedrive_aux\Datos UNASEV\salida_columnas.csv'

    conservar_columnas_pandas(directorio_entrada, archivo_csv_entrada, archivo_csv_salida)

    mapeo()

    # Definir el sistema de coordenadas geográficas (latitud, longitud)
    proj_latlon = Proj(proj='latlong', datum='WGS84')

    # Llamar a la función con tus archivos de entrada y salida
    convertir_utm_a_geograficas('salida_columnas_transformado.csv', 'salida_geograficas.csv')

    salida_geograficas = pd.read_csv('salida_geograficas.csv')
    id = 1

    #func
    mi_diccionario = reduccion_datos(salida_geograficas)


    for index, row in mi_diccionario.items():
        # Convierte la fila a un diccionario para facilitar la manipulación
        data_dict = row

        # Verifica si ya existe un documento con el mismo ID en la colección 'accidentes'
        doc_ref = db.collection('accidentes').document(str(index))

        # Guarda el diccionario como documento en la colección 'accidentes'
        doc_ref.set(data_dict)
        print(f'Documento {index} guardado en la base de datos.')



        """
        existing_doc = db.collection('accidentes').document(str(id)).get()

        if not existing_doc.exists:
            # Si no existe, agrega el documento a la colección 'accidentes' con la ID personalizada
            db.collection('accidentes').document(str(id)).set(data_dict)
            print(f"Documento con ID {id} agregado")
        else:
            print(f"Documento con ID {id} ya existe. Saltando la adición.")
        """
