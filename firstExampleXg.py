import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Ejemplo de datos de calificaciones de estudiantes
data = {
    'Nota_Part1': [4, 5, 3, 6, 5, 7, 2, 4],
    'Nota_Part2': [7, 6, 4, 8, 7, 9, 3, 5],
    'Examen_Final': [0, 0, 0, 1, 0, 1, 0, 0],
}

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
