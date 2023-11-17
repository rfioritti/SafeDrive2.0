from firebase_admin import credentials, firestore, initialize_app

# Configura las credenciales de Firebase
cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
initialize_app(cred)

# Obtén una referencia a la base de datos Firestore
db = firestore.client()

# Datos a insertar en la base de datos
datos_recorridos = [
    {
        "id_recorrido": 1,
        "z_inicial": 100,
        "z_final": 150,
        "fecha": "2023-11-16",
        "velocidad_promedio": 60,
        "velocidad_maxima": 80,
        "sintomas": ["mareo", "náuseas"],
        "frenadas_bruscas": 2,
        "aceleraciones_bruscas": 1,
        "km_recorridos": 30,
        "tiempo_recorrido": "02:30:00",
        "fecha_evento": "2023-11-16T08:00:00",
        "evento": "accidente",
        "dist": 10,
        "dor": 7
    }
]

# Inserta los datos en la colección "recorridos"
for recorrido in datos_recorridos:
    db.collection('recorridos').document(str(recorrido["id_recorrido"])).set(recorrido)

print("Datos insertados en la base de datos.")
