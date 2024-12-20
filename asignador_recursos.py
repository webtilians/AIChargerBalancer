import queue
import time
from sklearn.linear_model import LinearRegression
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split
import os
class DemandPredictor:
    def __init__(self, model_path="demand_predictor_model.h5"):
        self.model_path = model_path
        self.model = self.cargar_o_crear_modelo()
        self.trained = False

    def cargar_o_crear_modelo(self):
        """Carga el modelo desde el archivo si existe, de lo contrario crea uno nuevo."""
        if os.path.exists(self.model_path):
            model = keras.models.load_model(self.model_path)
            self.trained = True
            print("Modelo cargado desde el archivo.")
            return model
        else:
            return self.crear_modelo()

    def crear_modelo(self):
        """Crea el modelo de red neuronal."""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(4,)),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def train(self, X, y, epochs=100, validation_split=0.2):
        """Entrena el modelo de red neuronal.

        Args:
            X (list of lists): Lista de características de entrenamiento.
            y (list): Lista de valores de demanda de recursos.
            epochs (int): Número de épocas de entrenamiento.
            validation_split (float): Porcentaje de datos para validación.
        """
        X = np.array(X)
        y = np.array(y)

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)

        self.model.fit(X_train, y_train, epochs=epochs, validation_data=(X_val, y_val))
        self.trained = True
        print("Modelo entrenado.")

        # Guardar el modelo entrenado
        self.model.save(self.model_path)
        print(f"Modelo guardado en {self.model_path}")


class ServidorSimulado:
    def __init__(self, num_servidores_inicial, demand_predictor):
        self.num_servidores_max = 5
        self.servidores = [ServidorSimulado(i) for i in range(num_servidores_inicial)]
        self.demand_predictor = demand_predictor
        self.umbral_escalado_superior = 5
        self.umbral_escalado_inferior = 1
        self.cola_solicitudes = queue.Queue()
        self.intervalo_impresion = 10  # Imprimir cada 10 segundos
        self.ultimo_tiempo_impresion = time.time()

    def procesar_solicitud(self, caracteristicas, timestamp):
        """
        Simula el procesamiento de una solicitud y actualiza la carga del servidor.
        """
        if self.arrancando:
            print(f"Servidor {self.id}: No se puede procesar la solicitud, el servidor está arrancando.")
            return

        print(f"Servidor {self.id}: Procesando solicitud. Características: {caracteristicas}")

        # Utilizar la longitud como un estimado del tiempo de procesamiento
        tiempo_procesamiento = caracteristicas["longitud"] * 0.01

        self.carga += tiempo_procesamiento
        time.sleep(tiempo_procesamiento)
        self.carga -= tiempo_procesamiento

        # Calcular y registrar métricas de latencia
        tiempo_respuesta = time.time() - timestamp
        print(f"Servidor {self.id}: Solicitud completada. Tiempo de respuesta: {tiempo_respuesta:.4f} segundos. Carga actual: {self.carga:.2f}")

class AsignadorRecursos:
    def __init__(self, num_servidores_inicial, demand_predictor):
        self.num_servidores_max = 5
        self.servidores = [ServidorSimulado(i) for i in range(num_servidores_inicial)]
        self.demand_predictor = demand_predictor
        self.umbral_escalado_superior = 5
        self.umbral_escalado_inferior = 1
        self.cola_solicitudes = queue.Queue()

    def asignar(self, user_id, caracteristicas):
        """
        Asigna una solicitud a la cola.
        """
        predicted_demand = self.demand_predictor.predict(caracteristicas)
        self.cola_solicitudes.put((user_id, caracteristicas, predicted_demand, time.time()))  # Añadir timestamp
        print(f"Solicitud de usuario {user_id} encolada. Demanda predicha: {predicted_demand:.2f}")

        # Comprobar si hay servidores libres y procesar solicitudes
        self.procesar_solicitudes()

        # Comprobar si es necesario escalar
        self.comprobar_escalado()

        return "encolada"

    def procesar_solicitudes(self):
        """
        Procesa solicitudes de la cola, asignándolas a servidores libres.
        """
        servidor_elegido = min(self.servidores, key=lambda s: s.carga)
        # Solo asignar la solicitud si el servidor no está arrancando y hay solicitudes en la cola
        if not servidor_elegido.arrancando and not self.cola_solicitudes.empty():
            user_id, caracteristicas, predicted_demand, timestamp = self.cola_solicitudes.get()
            print(f"Asignando solicitud de usuario {user_id} al servidor {servidor_elegido.id} con demanda predicha de: {predicted_demand}")
            servidor_elegido.procesar_solicitud(caracteristicas, timestamp)
            self.cola_solicitudes.task_done()

    def crear_servidor(self):
        """
        Añade un nuevo servidor a la lista de servidores.
        """
        if len(self.servidores) < self.num_servidores_max:
            nuevo_servidor_id = len(self.servidores)
            self.servidores.append(ServidorSimulado(nuevo_servidor_id))
            print(f"Nuevo servidor creado con ID {nuevo_servidor_id}. Total de servidores: {len(self.servidores)}")
        else:
            print(f"No se pueden crear más servidores. Se ha alcanzado el límite máximo de {self.num_servidores_max} servidores.")

    def eliminar_servidor(self):
        """
        Elimina un servidor de la lista de servidores, si hay más de uno.
        """
        if len(self.servidores) > 1:
            servidor_a_eliminar = self.servidores.pop()
            print(f"Servidor {servidor_a_eliminar.id} eliminado. Total de servidores: {len(self.servidores)}")
        else:
            print("No se pueden eliminar más servidores. Se ha alcanzado el mínimo de 1 servidor.")

    def comprobar_escalado(self):
      """
      Comprueba si la carga total de los servidores supera o cae por debajo de los umbrales definidos.
      Escala el número de servidores en consecuencia.
      """
      carga_total = sum(s.carga for s in self.servidores if not s.arrancando)
      num_servidores_activos = sum(1 for s in self.servidores if not s.arrancando)

      print(f"Carga total del sistema: {carga_total:.2f}, servidores activos: {num_servidores_activos}")

      if carga_total > self.umbral_escalado_superior and len(self.servidores) < self.num_servidores_max:
          self.crear_servidor()
      elif carga_total < self.umbral_escalado_inferior and len(self.servidores) > 1:
          self.eliminar_servidor()
          self.imprimir_estado()
    
    def imprimir_estado(self):
        """Imprime el estado actual de los servidores y la cola de solicitudes."""
        ahora = time.time()
        if ahora - self.ultimo_tiempo_impresion > self.intervalo_impresion:
            print("\n--- Estado del Sistema ---")
            for servidor in self.servidores:
                print(f"Servidor {servidor.id}: Carga actual = {servidor.carga:.2f}, Arrancando = {servidor.arrancando}")
            print(f"Longitud de la cola de solicitudes: {self.cola_solicitudes.qsize()}")
            print("--------------------------\n")
            self.ultimo_tiempo_impresion = ahora
          