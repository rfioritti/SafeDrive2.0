import xgboost as xgb
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="xgboost")

# Cargar tus datos desde un archivo CSV (reemplaza 'datos.csv' con tu archivo de datos)
data = pd.read_csv('/home/ubuntu/SafeDrive2.0/simulacion_datos/datos.csv')

# Dividir el conjunto de datos en características (X) y etiquetas (y)
# X = data[['zini', 'zfin', 'velProm', 'velMax', 'tRec', 'AB', 'FB', 'kmRec', 'sints']]
X = data[['z_inicial', 'z_final', 'velocidad_promedio', 'velocidad_maxima', 'tiempo_recorrido', 'aceleraciones_bruscas', 'frenadas_bruscas', 'km_recorridos', 'sintomas']]
y_dorm = data['dor']
y_distraccion = data['dist']

# Dividir el conjunto de datos en conjuntos de entrenamiento y prueba para la variable "dorm"
X_entrenamiento, X_prueba, y_dorm_entrenamiento, y_dorm_prueba = train_test_split(X, y_dorm, test_size=0.2, random_state=42)

# Crear un clasificador XGBoost para la variable "dorm"
modelo_dorm = xgb.XGBClassifier()
modelo_dorm.fit(X_entrenamiento, y_dorm_entrenamiento)
y_dorm_prediccion = modelo_dorm.predict(X_prueba)

# Calcular la precisión para "dorm"
precision_dorm = accuracy_score(y_dorm_prueba, y_dorm_prediccion)
print(f"Precisión para dormir: {precision_dorm * 100:.2f}%")

# Dividir el conjunto de datos en conjuntos de entrenamiento y prueba para la variable "distraccion"
X_entrenamiento, X_prueba, y_distraccion_entrenamiento, y_distraccion_prueba = train_test_split(X, y_distraccion, test_size=0.2, random_state=42)

# Crear un clasificador XGBoost para la variable "distraccion"
modelo_distraccion = xgb.XGBClassifier()
modelo_distraccion.fit(X_entrenamiento, y_distraccion_entrenamiento)
y_distraccion_prediccion = modelo_distraccion.predict(X_prueba)

# Calcular la precisión para "distraccion"
precision_distraccion = accuracy_score(y_distraccion_prueba, y_distraccion_prediccion)
print(f"Precisión para distracción: {precision_distraccion * 100:.2f}%")

# Guardar los modelos en archivos separados
joblib.dump(modelo_dorm, 'modelo_prediccion_dorm.pkl')
joblib.dump(modelo_distraccion, 'modelo_prediccion_distraccion.pkl')
