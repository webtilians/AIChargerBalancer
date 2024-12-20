import requests
import time
import random

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_intermedio_1", "user_intermedio_2", "user_intermedio_3"]  # Usuarios intermedios
texts = {
    "simple": ["Consulta sobre mi plan", "Duda sobre la factura", "Cambiar mi suscripción"],
    "compleja": ["Análisis de datos de mi cuenta", "Informe de uso del último mes", "Solicitud de integración con API"],
    "codigo": ["Ejecución de script simple", "Prueba de API"]  # Ocasionalmente ejecutan código
}

def send_request():
    while True:
        user_id = random.choice(users)
        request_type = random.choices(["simple", "compleja", "codigo"], weights=[0.4, 0.4, 0.2])[0]  # 40% simple, 40% compleja, 20% código
        text = random.choice(texts[request_type])
        data = {'user_id': user_id, 'texto': text}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
        time.sleep(random.uniform(1, 3))  # Pausa moderada

if __name__ == "__main__":
    send_request()