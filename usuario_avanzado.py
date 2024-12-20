import requests
import time
import random

url = 'http://127.0.0.1:5000/solicitud'

users = ["user_avanzado_1", "user_avanzado_2", "user_avanzado_3"]  # Usuarios avanzados
texts = {
    "compleja": ["Análisis avanzado de datos", "Informe de rendimiento personalizado", "Predicciones de mercado", "Optimización de modelo de ML"],
    "codigo": ["Ejecución de código Python complejo", "Automatización de tareas con scripts", "Integración de API avanzada", "Depuración de código"]
}

tiempos_respuesta = []

def send_request():
    while True:
        user_id = random.choice(users)
        request_type = random.choices(["compleja", "codigo"], weights=[0.6, 0.4])[0]  # 60% compleja, 40% código
        text = random.choice(texts[request_type])
        data = {'user_id': user_id, 'texto': text}
        try:
            inicio = time.time()
            response = requests.post(url, json=data)
            response.raise_for_status()
            fin = time.time()
            tiempo_respuesta = fin - inicio
            tiempos_respuesta.append(tiempo_respuesta)
            print(f"Solicitud enviada por {user_id} ({request_type}): {text}. Respuesta: {response.status_code} - {response.json()}. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos")
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
        time.sleep(random.uniform(0.5, 1.5))  # Pausa corta

def calculate_statistics():
    if tiempos_respuesta:
        promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
        maximo = max(tiempos_respuesta)
        minimo = min(tiempos_respuesta)
        print(f"\nEstadísticas de tiempos de respuesta (Usuario Avanzado):")
        print(f"  Promedio: {promedio:.4f} segundos")
        print(f"  Máximo: {maximo:.4f} segundos")
        print(f"  Mínimo: {minimo:.4f} segundos")
    else:
        print("No se registraron tiempos de respuesta (Usuario Avanzado).")

if __name__ == "__main__":
    try:
        send_request()
    except KeyboardInterrupt:
        print("Simulación finalizada.")
        calculate_statistics()
        requests.post('http://127.0.0.1:5000/actualizar_perfiles')