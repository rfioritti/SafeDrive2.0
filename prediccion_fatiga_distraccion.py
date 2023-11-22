import xgboost as xgb
import joblib
import pandas as pd

def predecir_probabilidades_fatiga_distraccion(recorridos):
    # Cargar los modelos entrenados
    modelo_dorm = joblib.load('modelo_prediccion_dorm.pkl')
    modelo_distraccion = joblib.load('modelo_prediccion_distraccion.pkl')

    # Proporciona el recorrido como datos de entrada para las predicciones
    # Asegúrate de que el recorrido tenga las mismas características que se utilizaron durante el entrenamiento
    recorrido = recorridos[0]
    datos_recorrido = pd.DataFrame({
        'z_inicial': [recorrido['z_inicial']],
        'z_final': [recorrido['z_final']],
        'velocidad_promedio': [recorrido['velocidad_promedio']],
        'velocidad_maxima': [recorrido['velocidad_maxima']],
        'tiempo_recorrido': [recorrido['tiempo_recorrido']],
        'aceleraciones_bruscas': [recorrido['aceleraciones_bruscas']],
        'frenadas_bruscas': [recorrido['frenadas_bruscas']],
        'km_recorridos': [recorrido['km_recorridos']],
        'sintomas': [recorrido['sintomas']]
    })

    # Realiza predicciones de probabilidad para "dormir" y "distracción"
    probabilidad_dorm = modelo_dorm.predict_proba(datos_recorrido)
    probabilidad_distraccion = modelo_distraccion.predict_proba(datos_recorrido)

    # Extrae la probabilidad de que ocurran los eventos
    probabilidad_dorm = probabilidad_dorm[:, 1]  # Probabilidad de "dormir"
    probabilidad_distraccion = probabilidad_distraccion[:, 1]  # Probabilidad de "distracción"
   # print("------")
   # print("prob dorm: "+ str(probabilidad_dorm[0])+"  prob distraccion: "+str(probabilidad_distraccion[0]))

    return probabilidad_dorm[0], probabilidad_distraccion[0]
    
'''
recorrido_ejemplo = {
    'zini': 1,          # Valor de zini
    'zfin': 2,          # Valor de zfin
    'velProm': 60,        # Valor de velProm
    'velMax': 80,         # Valor de velMax
    'tRec': 30,           # Valor de tRec
    'AB': 0,              # Valor de AB
    'FB': 1,              # Valor de FB
    'kmRec': 10,          # Valor de kmRec
    'sints': 2          # Valor de sints
}

predecir_probabilidades_fatiga_distraccion(recorrido_ejemplo) 
'''