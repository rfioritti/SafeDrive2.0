import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

recorridos = pd.read_csv(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/recorridos_simulados.csv') #COLOCAR LA RUTA DEL CSV DE LOS RECORRIDOS
eventos = pd.read_csv(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/eventos_simulados.csv') #COLOCAR LA RUTA DEL CSV DE LOS EVENTOS
    
departamentos = gpd.read_file(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson') #FUENTE: https://github.com/alotropico/uruguay.geo


# In[5]:


#EVALUACION DE DISTRACCIONES Y DORMIDOS
# tiempo en minutos
def distracciones_eval(distracciones, tiempo):
    if distracciones / tiempo > 0.05:
        return True
    else:
        return False
    
def dormidos_eval(dormido):
    if dormido >= 1:
        return True
    else:
        return False


# In[6]:


#PROCESO AUTOMATICO DE LECTURA Y PREPARACION INICIAL
  
eventos.rename(columns = {'id_recorrido_id':'id_recorrido'}, inplace = True) #ajuste para merge
    
eventos_recorridos = pd.merge(recorridos, eventos, how="outer", on=["id_recorrido"]) #merge de datasets
#orden por recorrido y luego fecha de eventos
eventos_recorridos = eventos_recorridos.sort_values(['id_recorrido', 'fecha_hora'], ascending = [True, True])
    
#quedarse solo con el primer y ultimo evento de cada recorrido
primer_evento = eventos_recorridos.groupby('id_recorrido').first()
ultimo_evento = eventos_recorridos.groupby('id_recorrido').last()

eventos_filtrados = pd.concat([primer_evento, ultimo_evento])
eventos_filtrados = eventos_filtrados.sort_values(['id_recorrido', 'fecha_hora'], ascending = [True, True])
    
#analisis de distracciones y dormido para pasarlos a boolean
eventos_filtrados['dist'] = eventos_filtrados.apply(lambda row: distracciones_eval(row['distracciones'], row['tiempo_recorrido']), axis=1)
eventos_filtrados['dor'] = eventos_filtrados['dormido'].apply(dormidos_eval)
    
#utilizar las coordenadas para determinar departamentos o exterior
eventos_filtrados['departamento'] = ""

# Iteraracion por filas del dataset y asignacion
for index, row in eventos_filtrados.iterrows():
    point = Point(row['longitud'], row['latitud'])  # Crea un objeto Point con las coordenadas
    departamento = departamentos[departamentos.contains(point)]['NAME_1']  # busca el punto dentro del dataset de geopandas
    if not departamento.empty:
        eventos_filtrados.at[index, 'departamento'] = departamento.values[0]
    else:
        eventos_filtrados.at[index, 'departamento'] = 20
        
#se agrupa por id y se crea una lista de los departamentos para cada id
recorridos_completos = eventos_filtrados.groupby('id_recorrido')['departamento'].apply(list).reset_index()

#se crean las columnas z_inicial y z_final
recorridos_completos['z_inicial'] = recorridos_completos['departamento'].apply(lambda x: x[0]) #primer valor de la lista
recorridos_completos['z_final'] = recorridos_completos['departamento'].apply(lambda x: x[-1]) #ultimo valor de la lista

# Combina las demás columnas
recorridos_completos = recorridos_completos.merge(eventos_filtrados.drop(columns=['departamento']), on='id_recorrido', how='left')
    
#eliminacion de columnas innecesarias y renombre de restantes
recorridos_completos = recorridos_completos.drop(columns=['fecha_fin', 'fecha_hora','evento','distracciones', 'dormido', 'matricula_id', 'id_evento', 'velocidad', 'latitud', 'longitud', 'departamento'])
recorridos_completos.rename(columns = {'fecha_inicio':'fecha', 'vel_promedio':'vel_prom'}, inplace = True)
    
#se quitan las id duplicadas
recorridos_completos.drop_duplicates(subset='id_recorrido', keep='first', inplace=True)

recorridos_completos.set_index('id_recorrido')

for index, row in recorridos_completos.iterrows():
    # Convierte la fila a un diccionario para facilitar la manipulación
    data_dict = row.to_dict()

    # Agrega el documento a la colección 'miColeccion' en Firebase
    db.collection('recorridos').add(data_dict)
    
recorridos_completos.to_csv(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/datos.csv') #EXPORTAR CSV / AJUSTAR LA RUTA DE SALIDA


