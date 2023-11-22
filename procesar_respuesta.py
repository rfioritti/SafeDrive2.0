import geopandas as gpd
from shapely.geometry import Point

departamentos = gpd.read_file(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/uruguay.geojson')

def perfilar_consulta(consulta_json):
    
    
    dist = consulta_json['distracciones'] / consulta_json['tiempo_recorrido'] > 0.05
    dor = consulta_json['dormido'] > 0

    z_ini = 0
    z_fin = 0

    point_ini = Point(consulta_json['longitud_inicio'], consulta_json['latitud_inicio'])  # Crea un objeto Point con las coordenadas
    departamento_ini = departamentos[departamentos.contains(point_ini)]['NAME_1']  # busca el punto dentro del dataset de geopandas
    if not departamento_ini.empty:
        z_ini = departamento_ini.values[0]
    else:
        z_ini = 20

    point_fin = Point(consulta_json['longitud_fin'], consulta_json['latitud_fin'])  # Crea un objeto Point con las coordenadas
    departamento_fin = departamentos[departamentos.contains(point_fin)]['NAME_1']  # busca el punto dentro del dataset de geopandas
    if not departamento_fin.empty:
        z_fin = departamento_fin.values[0]
    else:
        z_fin = 20

    
    recorrido = [
        {
            'id_recorrido' : consulta_json['id_recorrido'],
            'z_inicial' : z_ini,
            'z_final' : z_fin,
            'fecha' : consulta_json['fecha_inicio'],
            'velocidad_promedio' : consulta_json['velocidad_promedio'],
            'velocidad_maxima' : consulta_json['velocidad_maxima'],
            'tiempo_recorrido' : consulta_json['tiempo_recorrido'],
            'aceleraciones_bruscas' : consulta_json['aceleraciones_bruscas'],
            'frenadas_bruscas' : consulta_json['frenadas_bruscas'],
            'km_recorridos' : consulta_json['km_recorridos'],
            'sintomas' : consulta_json['sintomas'],
            'dist': dist,
            'dor' : dor
        }
    ]

    return recorrido