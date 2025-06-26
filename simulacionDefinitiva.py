import socket
import struct
import time
import random

SERVER_IP = "212.128.45.131"
SERVER_PORT = 8085

sensor_id = 0x7EA1 
sampling_period = 1 / 32000.0

# Cantidad de muestras (int16: 2 bytes cada una)
samples_time = 32000  # 32000 muestras en un segundo
samples_freq = 0      # No se generan muestras de frecuencia
len_time = samples_time * 2
len_freq = samples_freq * 2

def limitar_int16(valor):
    return max(min(int(valor), 32767), -32768)

initial_timestamp = int(time.time())
counter = 0

while True:
    timestamp = initial_timestamp + counter
    counter += 1

    media = 20000
    desviacion = 3000

    time_data = [limitar_int16(random.gauss(media, desviacion)) for _ in range(samples_time)]
    freq_data = []  # No se generan datos de frecuencia

    header = struct.pack('<IQHHf', sensor_id, timestamp, len_time, len_freq, sampling_period)
    payload = struct.pack(f'<{samples_time}h', *time_data) + struct.pack(f'<{samples_freq}h', *freq_data)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(header)
            print(f"Header size: {len(header)} bytes")  # Debería ser 20
            s.sendall(b'\x00\x00')  # Flush de 2 bytes
            s.sendall(payload)
            print(f"Datos enviados correctamente a las {time.strftime('%X')} (timestamp: {timestamp}) | Payload bytes: {len(payload)}")
    except Exception as e:
        print(f"Error al enviar datos: {e}")
    time.sleep(1)
