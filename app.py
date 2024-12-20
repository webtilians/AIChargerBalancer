from flask import Flask, request, jsonify
from gestor_usuarios import GestorUsuarios
from analizador_solicitudes import AnalizadorSolicitudes
from asignador_recursos import AsignadorRecursos, DemandPredictor
import numpy as np
import time


app = Flask(__name__)

# Instanciar los componentes
gestor_usuarios = GestorUsuarios()
analizador_solicitudes = AnalizadorSolicitudes()
demand_predictor = DemandPredictor()

# Datos de entrenamiento de ejemplo (puedes agregar más o usar un archivo CSV)
training_data = [
    ({"longitud": len("Consulta general"), "tipo": "simple"}, 1),
    ({"longitud": len("Análisis de datos y predicciones"), "tipo": "compleja"}, 3),
    ({"longitud": len("Ejecución de código Python"), "tipo": "codigo"}, 5),
    ({"longitud": len("Otra consulta simple"), "tipo": "simple"}, 1),
    ({"longitud": len("Solicitud compleja de análisis"), "tipo": "compleja"}, 4),
    ({"longitud": len("Otro ejemplo de código"), "tipo": "codigo"}, 6)  # Nuevo dato
]

# Preparar los datos para el entrenamiento
X_train = []
y_train = []
for features, demand in training_data:
    feature_vector = [
        features["longitud"],
        1 if features["tipo"] == "simple" else 0,
        1 if features["tipo"] == "compleja" else 0,
        1 if features["tipo"] == "codigo" else 0
    ]
    X_train.append(feature_vector)
    y_train.append(demand)

# Entrenar el modelo de predicción de demanda
demand_predictor.train(X_train, y_train, epochs=100) #aumentamos las epochs

# Crear la instancia del asignador de recursos
asignador_recursos = AsignadorRecursos(num_servidores_inicial=1, demand_predictor=demand_predictor)

@app.route('/solicitud', methods=['POST'])
def procesar_solicitud():
    """
    Recibe una solicitud de usuario, la analiza, asigna un perfil y la enruta a un servidor.
    """
    try:
        data = request.get_json()

        # Validar la entrada
        if not data or 'user_id' not in data or 'texto' not in data:
            return jsonify({'error': 'Datos de solicitud no válidos'}), 400

        user_id = data['user_id']
        texto_solicitud = data['texto']

        # Analizar la solicitud
        caracteristicas = analizador_solicitudes.analizar(texto_solicitud)

        # Registrar la solicitud en el historial del usuario
        gestor_usuarios.registrar_solicitud(user_id, caracteristicas)

        # Obtener el perfil del usuario
        perfil = gestor_usuarios.obtener_perfil(user_id)

        # Asignar la solicitud a un servidor
        servidor_id = asignador_recursos.asignar(user_id, caracteristicas)

        # Actualizar el perfil del usuario basado en su historial
        gestor_usuarios.actualizar_perfil(user_id)

        return jsonify({
            'mensaje': 'Solicitud procesada correctamente',
            'user_id': user_id,
            'perfil': perfil,
            'servidor_asignado': servidor_id,
            'caracteristicas': caracteristicas
        }), 200

    except Exception as e:
        print(f"Error al procesar la solicitud: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Nueva ruta para actualizar todos los perfiles
@app.route('/actualizar_perfiles', methods=['POST'])
def actualizar_perfiles():
    try:
        gestor_usuarios.actualizar_perfiles()
        return jsonify({'mensaje': 'Perfiles de usuario actualizados correctamente'}), 200
    except Exception as e:
        print(f"Error al actualizar perfiles: {e}")
        return jsonify({'error': 'Error interno del servidor al actualizar perfiles'}), 500

if __name__ == '__main__':
    app.run(debug=True)