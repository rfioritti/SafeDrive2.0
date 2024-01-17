from firebase_admin import credentials, firestore, initialize_app

# Configura las credenciales de Firebase
#cred = credentials.Certificate('/home/ubuntu/keys/safedrive-aux-firebase-adminsdk-5e35m-dd2ee6fa20.json')
#initialize_app(cred)

# Obtén una referencia a la base de datos Firestore
#db = firestore.client()

#Recibe un array de JSON
def guardar_recorrido(recorrido_json, db):
    
    try:
        # Inserta los datos en la colección "recorridos"
        for recorrido in recorrido_json:
            db.collection('recorridos').document(str(recorrido["id_recorrido"])).set(recorrido)
        
        return {"success": True, "message": "Datos guardados correctamente"}

    except Exception as e:
        return {"success": False, "message": f"Error al guardar datos en Firebase: {str(e)}"}

# # Datos a insertar en la base de datos
# datos_recorridos = [
#     {
#         'id_recorrido': 2,
#         'z_inicial': 1,
#         'z_final': 7,
#         'fecha': "2023-11-16",
#         'velocidad_promedio': 600,
#         'velocidad_maxima': 80,
#         'sintomas': 1,
#         'frenadas_bruscas': 2,
#         'aceleraciones_bruscas': 1,
#         'km_recorridos': 30,
#         'tiempo_recorrido': 120,
#         'dist': 1,
#         'dor': 1
#     }
# ]