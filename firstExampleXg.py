import xgboost as xgb
import pandas as pd
import joblib
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Ejemplo de datos de calificaciones de estudiantes

"""
data = {
    'Nota_Part1': [4, 5, 3, 6, 5, 7, 2, 4],
    'Nota_Part2': [7, 6, 4, 8, 7, 9, 3, 5],
    'Examen_Final': [0, 0, 0, 1, 0, 1, 0, 0],
}
"""
# Crear una lista de datos ficticios de notas para la Parte 1 y la Parte 2
notas_part1 = [random.randint(0, 12) for _ in range(50)]  # Generar 100 notas aleatorias entre 0 y 10
notas_part2 = [random.randint(0, 12) for _ in range(50)]

# Calcular la suma de las notas de la Parte 1 y la Parte 2
suma_notas = [nota1 + nota2 for nota1, nota2 in zip(notas_part1, notas_part2)]

# Crear una lista de etiquetas (0 para no pasar, 1 para pasar) basada en la condición
etiquetas = [1 if suma > 18 and random.random() <= 0.75 else 0 for suma in suma_notas]

# Crear un DataFrame con los datos
data = {
    'Nota_Part1': notas_part1,
    'Nota_Part2': notas_part2,
    'Pasar': etiquetas,
}
print("================================================")
print(notas_part1)
print(notas_part2)
print("------------------------------------------------")
print("------------------------------------------------")
print(etiquetas)
print("================================================")
# Crear un DataFrame a partir de los datos de ejemplo
df = pd.DataFrame(data)

# Dividir el conjunto de datos en características (X) y etiquetas (y)
X = df[['Nota_Part1', 'Nota_Part2']]
y = df['Examen_Final']

# Dividir el conjunto de datos en conjuntos de entrenamiento y prueba
X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)

# Crear un clasificador XGBoost
modelo = xgb.XGBClassifier()

# Entrenar el modelo con los datos de entrenamiento
modelo.fit(X_entrenamiento, y_entrenamiento)

# Hacer predicciones en los datos de prueba
y_prediccion = modelo.predict(X_prueba)

# Calcular la precisión
precision = accuracy_score(y_prueba, y_prediccion)
print(f"Precisión: {precision * 100:.2f}%")

# Guardar el modelo en un archivo
joblib.dump(modelo, 'modelo_entrenado.pkl')
