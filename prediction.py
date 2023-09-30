# Supongamos que queremos predecir para un estudiante con una calificación de 4 en la primera parte y 8 en la segunda parte.
import pandas as pd
import joblib

# Cargar el modelo entrenado desde el archivo
modelo = joblib.load('modelo_entrenado.pkl')

nueva_data = {
    'Nota_Part1': [4],
    'Nota_Part2': [8],
}

# Crear un DataFrame con la nueva data
nuevo_df = pd.DataFrame(nueva_data)

# Realizar la predicción utilizando el modelo XGBoost entrenado
probabilidad_prediccion = modelo.predict_proba(nuevo_df)

# La probabilidad de obtener una calificación de 6 o más en el examen final se encuentra en probabilidad_prediccion[0][1]
probabilidad = probabilidad_prediccion[0][1] * 100  # Multiplicar por 100 para expresarla en porcentaje

print(f"La probabilidad de obtener una calificación de 6 o más en el examen final es del {probabilidad:.2f}%")
