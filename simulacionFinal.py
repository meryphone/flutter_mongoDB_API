import socket
import struct
import time
import random

# IP y puerto del receptor TCP
SERVER_IP = "212.128.45.131"
SERVER_PORT = 8085

# Configuración del sensor simulado
sensor_id = 0x7EA2  # ID entero de sensor (usar valores distintos si simulas varios)
sampling_period = 1 / 32000.0  # en segundos (float32)

# Cantidades de muestras (en bytes = int16 * 2)
samples_time = 16384  # equivalente a 32768 bytes (como en imagen)
samples_freq = 1      # para simular 2 bytes espectrales
len_time = samples_time * 2
len_freq = samples_freq * 2

# Asegura valores dentro del rango de int16
def limitar_int16(valor):
    return max(min(int(valor), 32767), -32768)

# Timestamp inicial
initial_timestamp = int(time.time())
counter = 0

while True:
    timestamp = initial_timestamp + counter
    counter += 1

    # Generar datos simulados (gaussianos)
    media = 20000
    desviacion = 3000

    time_data = [limitar_int16(random.gauss(media, desviacion)) for _ in range(samples_time)]
    freq_data = [limitar_int16(random.gauss(media, desviacion)) for _ in range(samples_freq)]

    # Crear header: <IQHHf>
    # I = sensor_id (uint32), Q = timestamp (uint64), H = len_time (uint16), H = len_freq (uint16), f = sampling_period (float32)
    header = struct.pack('<IQHHf', sensor_id, timestamp, len_time, len_freq, sampling_period)

    # Crear payload
    payload_time = struct.pack(f'<{samples_time}h', *time_data)
    payload_freq = struct.pack(f'<{samples_freq}h', *freq_data)
    payload = payload_time + payload_freq

    # Enviar por socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(header + payload)
            print(f"Datos enviados - timestamp: {timestamp}, muestras: {samples_time}")
    except Exception as e:
        print(f"Error al enviar datos: {e}")

    time.sleep(1)

