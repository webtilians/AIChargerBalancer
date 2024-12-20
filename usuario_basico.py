import requests
import time
import random

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_basico_1", "user_basico_2", "user_basico_3"]  # Usuarios básicos
texts = ["Consulta general", "Duda sobre el servicio", "Información de contacto"]

def send_request():
    while True:
        user_id = random.choice(users)
        text = random.choice(texts)
        data = {'user_id': user_id, 'texto': text}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print(f"Solicitud enviada por {user_id}: {text}. Respuesta: {response.status_code} - {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
        time.sleep(random.uniform(2, 5))  # Pausa más larga para usuarios básicos

if __name__ == "__main__":
    send_request()