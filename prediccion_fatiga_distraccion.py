import xgboost as xgb
import joblib
import pandas as pd

def predecir_probabilidades_fatiga_distraccion(recorrido):
    # Cargar los modelos entrenados
    modelo_dorm = joblib.load('modelo_prediccion_dorm.pkl')
    modelo_distraccion = joblib.load('modelo_prediccion_distraccion.pkl')

    # Proporciona el recorrido como datos de entrada para las predicciones
    # Asegúrate de que el recorrido tenga las mismas características que se utilizaron durante el entrenamiento
    datos_recorrido = pd.DataFrame({
        'zini': [recorrido['zini']],
        'zfin': [recorrido['zfin']],
        'velProm': [recorrido['velProm']],
        'velMax': [recorrido['velMax']],
        'tRec': [recorrido['tRec']],
        'AB': [recorrido['AB']],
        'FB': [recorrido['FB']],
        'kmRec': [recorrido['kmRec']],
        'sints': [recorrido['sints']]
    })

    # Realiza predicciones de probabilidad para "dormir" y "distracción"
    probabilidad_dorm = modelo_dorm.predict_proba(datos_recorrido)
    probabilidad_distraccion = modelo_distraccion.predict_proba(datos_recorrido)

    # Extrae la probabilidad de que ocurran los eventos
    probabilidad_dorm = probabilidad_dorm[:, 1]  # Probabilidad de "dormir"
    probabilidad_distraccion = probabilidad_distraccion[:, 1]  # Probabilidad de "distracción"
    print("------")
    print("prob dorm: "+ str(probabilidad_dorm[0])+"  prob distraccion: "+str(probabilidad_distraccion[0]))

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