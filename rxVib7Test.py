#!/usr/bin/python3

import struct
import socket
import threading
from pymongo import MongoClient

# Conexión a MongoDB
mongo_client = MongoClient("mongodb://sensorvib:claveSegura123@localhost:27017/vibraciones")
mongo_db = mongo_client["vibraciones"]
mongo_collection = mongo_db["test"]

_HOST = "0.0.0.0"
_PORT = 8085

def recv_exact(sock, n):
    """Recibe exactamente n bytes del socket."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def handle_client(client_socket, addr):
    print(f"Conexión entrante desde {addr}")
    try:
        while True:
            # 1) Leer 20 bytes de cabecera
            chunk = recv_exact(client_socket, 20)
            if not chunk:
                break

            # 2) Parsear el header con <IQHHf> (20 bytes)
            unpacked = struct.unpack('<IQHHf', chunk)
            parsed_header = {
                "name": None,
                "time": unpacked[1],
                "tags": {
                    "id": unpacked[0],
                    "len_time": unpacked[2],
                    "len_freq": unpacked[3],
                    "samp_period": unpacked[4],
                }
            }

            # 3) Leer 2 bytes extra de flush
            zero_flush = recv_exact(client_socket, 2)
            if not zero_flush:
                break

            # 4) Calcular _full_pck_size
            _full_pck_size = parsed_header["tags"]["len_time"] + parsed_header["tags"]["len_freq"]
            if _full_pck_size <= 0:
                print("Advertencia: Tamaño payload <= 0, se ignora.")
                break

            # 5) Recibir payload
            packet_data = recv_exact(client_socket, _full_pck_size)
            if not packet_data or len(packet_data) != _full_pck_size:
                print("Error: No se recibió el payload completo.")
                break

            # 6) Desempaquetar payload: int16 => 2 bytes por valor
            format_str = f'<{_full_pck_size // 2}h'
            payload_values = struct.unpack(format_str, packet_data)

            # 7) Guardar en Mongo
            doc = {
                "id": parsed_header["tags"]["id"],
                "timestamp": parsed_header["time"],
                "len_payload": parsed_header["tags"]["len_time"],
                "len_spect_payload": parsed_header["tags"]["len_freq"],
                "sampl_period": parsed_header["tags"]["samp_period"],
                "payload_values": list(payload_values)
            }
            mongo_collection.insert_one(doc)
            print(f"Documento insertado desde {addr} con {_full_pck_size} bytes de payload")

    except Exception as e:
        print(f"Error con {addr}: {e}")
    finally:
        client_socket.close()

def tcp_listen():
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((_HOST, _PORT))
    srv_socket.listen(5)
    print(f"Servidor TCP escuchando en {_PORT}")

    while True:
        client_socket, addr = srv_socket.accept()
        hilo = threading.Thread(target=handle_client, args=(client_socket, addr))
        hilo.start()

if __name__ == '__main__':
    tcp_listen()
