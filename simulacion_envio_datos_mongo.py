import socket
import struct
import time
import random

SERVER_IP = "212.128.45.131"
SERVER_PORT = 8085
PAYLOAD_LENGTH_SIZE = 16384
PAYLOAD_SPECT_LENGTH_SIZE = 16000

id = 0x7EA1
sampl_period = 1 / 32000.0
len_payload = PAYLOAD_LENGTH_SIZE * 2
len_spect_payload = PAYLOAD_SPECT_LENGTH_SIZE * 2

while True:
    timestamp = int(time.time())

    # Arrays de datos simulados
    continuous_data = [random.randint(0, 30000) for _ in range(PAYLOAD_LENGTH_SIZE)]
    spectral_data = [random.randint(-500, 500) for _ in range(PAYLOAD_SPECT_LENGTH_SIZE)]

    # Cabecera (nuevo formato)
    header = struct.pack('<HQHHf', id, timestamp, len_payload, len_spect_payload, sampl_period)

    # Payloads
    cont_bytes = struct.pack(f'<{PAYLOAD_LENGTH_SIZE}h', *continuous_data)
    spect_bytes = struct.pack(f'<{PAYLOAD_SPECT_LENGTH_SIZE}h', *spectral_data)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(header + cont_bytes + spect_bytes)
            print(f"Mensaje enviado correctamente. Timestamp: {timestamp}")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

    time.sleep(1)
