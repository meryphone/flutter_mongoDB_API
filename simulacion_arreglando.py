import socket
import struct
import time
import random

SERVER_IP = "212.128.45.131"
SERVER_PORT = 8085

# Cabecera fija
sensor_id = 0x7EA1
sampling_period = 1 / 32000.0

# Tamaños esperados por el servidor
len_time = 18400   # en bytes (9200 int16)
len_freq = 18318   # en bytes (9159 int16)

while True:
    # Nuevo timestamp para cada paquete
    timestamp = int(time.time())

    # Generar nuevos datos aleatorios uniformes entre 0 y 30000
    time_data = [random.randint(-1000, 1000) for _ in range(len_time // 2)]
    freq_data = [random.randint(-500, 500) for _ in range(len_freq // 2)]

    # Empaquetar
    header = struct.pack('<IQHHf', sensor_id, timestamp, len_time, len_freq, sampling_period)
    payload = struct.pack(f'<{len(time_data)}h', *time_data) + struct.pack(f'<{len(freq_data)}h', *freq_data)

    # Enviar
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(header + payload)
            print(f"Datos simulados enviados correctamente a las {time.strftime('%X')}")
            time.sleep(1)
    except Exception as e:
        print(f"Error al enviar datos: {e}")

    # Esperar 1 segundo
  

