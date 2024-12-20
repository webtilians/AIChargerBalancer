import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos desde el archivo CSV (ajusta el nombre del archivo si es necesario)
try:
    df = pd.read_csv("datos_simulacion.csv")

    # Convertir las columnas de tiempo a datetime
    df['tiempo_inicio'] = pd.to_datetime(df['tiempo_inicio'])
    df['tiempo_fin'] = pd.to_datetime(df['tiempo_fin'])

    # Calcular el tiempo de respuesta en segundos
    df['tiempo_respuesta'] = (df['tiempo_fin'] - df['tiempo_inicio']).dt.total_seconds()

    # Estadísticas descriptivas
    print(df.describe())

    # Visualización
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.hist(df['tiempo_respuesta'], bins=20)
    plt.xlabel('Tiempo de Respuesta (s)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Tiempos de Respuesta')

    plt.subplot(1, 2, 2)
    plt.plot(df['tiempo_inicio'], df['tiempo_respuesta'])
    plt.xlabel('Tiempo')
    plt.ylabel('Tiempo de Respuesta (s)')
    plt.title('Tiempo de Respuesta a lo Largo del Tiempo')

    plt.tight_layout()
    plt.show()

    # Análisis por tipo de usuario
    print("\nTiempos de respuesta por tipo de usuario:")
    print(df.groupby('user_id')['tiempo_respuesta'].mean())

    # Análisis por tipo de solicitud
    print("\nTiempos de respuesta por tipo de solicitud:")
    print(df.groupby('tipo_solicitud')['tiempo_respuesta'].mean())

except FileNotFoundError:
    print("El archivo CSV no se encontró. Asegúrate de que los scripts de prueba se están ejecutando y guardando los datos correctamente.")

except Exception as e:
    print(f"Ocurrió un error durante el análisis: {e}")