from firebase_admin import credentials, firestore, initialize_app
import pandas as pd

# Configura las credenciales de Firebase
cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
initialize_app(cred)

# Obtén una referencia a la base de datos Firestore
db = firestore.client()

def actualizar_csv_firebase():
    docs = db.collection("recorridos").stream()

    # Crear listas para almacenar datos de documentos
    ids = []
    data_dicts = []

    # Iterar sobre los documentos y almacenar la información en las listas
    for doc in docs:
        ids.append(doc.id)
        data_dicts.append(doc.to_dict())

    # Crear un DataFrame de pandas
    recorridos_firebase = pd.DataFrame(data_dicts, index=ids)

    recorridos_firebase.to_csv(r'/home/ubuntu/SafeDrive2.0/simulacion_datos/datos.csv')
