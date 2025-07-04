import os
import uvicorn
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from typing import List
from fastapi.responses import JSONResponse
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
import sys
import asyncio
import time
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

app = FastAPI()

# Enum para mensajes de error enviados al cliente
class ErrorMessages(str, Enum):
    UNEXPECTED_ERROR = "Error inesperado"
    DATA_NOT_FOUND = "Datos no encontrados"
    MONGO_TIMEOUT = "No se pudo conectar a MongoDB"

DESIRED_POINTS = 500  # Número de puntos a enviar tras downsampling
TIMEOUT = 5000  # Timeout para conexión a MongoDB

# Middleware CORS para permitir peticiones desde cualquier origen (útil en desarrollo)
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["https://tudominio.com"],  # Cambia esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta la carpeta de archivos estáticos (frontend)
app.mount("/grafica", StaticFiles(directory="frontend_dist", html=True), name="static")

# Conexión a MongoDB
MONGO_URI = os.getenv("MONGO_URI")
try:
    mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=TIMEOUT)
    mongo.admin.command("ping")  # Verifica conexión
    db = mongo["vibraciones"]
    collection = db["test"]
except errors.ServerSelectionTimeoutError as e:
    logging.error(f"No se pudo conectar a MongoDB: {e}")
    sys.exit(1)

def check_mongo_connection():
    try:
        mongo.admin.command("ping")
        return True
    except Exception as e:
        logging.warning("MongoDB ping failed: %s", e)
        return False

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)

manager = ConnectionManager()

def send_error(manager, websocket, error_enum: ErrorMessages, details: str = ""):
    return manager.send_json(websocket, {
        "error": error_enum,
        "details": details
    })

@app.get("/")
def home():
    if check_mongo_connection():
        return JSONResponse(
            content={"message": "API is running", "mongo_status": "connected"},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"message": "API is running", "mongo_status": ErrorMessages.MONGO_TIMEOUT},
            status_code=503
        )

@app.websocket("/vibraciones")
async def websocket_endpoint(websocket: WebSocket):
    # Maneja la conexión WebSocket con el cliente
    client_ip = websocket.client.host
    await manager.connect(websocket)
    logging.info(f"Cliente conectado desde IP: {client_ip}")

    current_sensor_id = None
    last_doc_id = None

    try:
        while True:
            # Espera mensajes del cliente para seleccionar sensor_id
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=0.1)
                if "sensor_id" in message:
                    new_sensor_id = int(message["sensor_id"])
                    doc_exists = collection.find_one({"id": new_sensor_id})
                    if not doc_exists:
                        await send_error(manager, websocket, ErrorMessages.DATA_NOT_FOUND,
                                         f"No se encontraron datos para el sensor {new_sensor_id}")
                        # No cerrar conexión, esperar otro sensor
                        current_sensor_id = None
                        last_doc_id = None
                        continue
                    # Si hay datos válidos, establecer como sensor actual
                    current_sensor_id = new_sensor_id
                    last_doc_id = None
                    logging.info(f"Cliente {client_ip} conectado a sensor {new_sensor_id}")
            except asyncio.TimeoutError:
                pass  # No hay mensaje nuevo

            if current_sensor_id is None:
                await asyncio.sleep(0.1)
                continue

            # Buscar documento más reciente para el sensor seleccionado
            doc = collection.find_one({"id": current_sensor_id}, sort=[("timestamp", -1)])
            if doc is not None:
                timestamp = doc["timestamp"]
                now = int(time.time())
                logging.debug(f"now: {now}, timestamp: {timestamp}, diferencia: {now - timestamp}")
                # Solo se envíe si el documento es reciente y es distinto al anterioir enviado
                if doc["_id"] != last_doc_id and (now - timestamp <= 3):
                    logging.debug(f"Enviando datos para sensor {current_sensor_id} (doc _id: {doc['_id']})")
                    last_doc_id = doc["_id"]
                    payload = doc["payload_values"]  # Datos de vibración
                    sampling_period = doc["sampl_period"]

                    total = len(payload)
                    step = max(1, total // DESIRED_POINTS)
                    filtered = payload[::step]

                    # Calcular máximo y mínimo de la tanda
                    max_value = max(payload) / 1000 if payload else None
                    min_value = min(payload) / 1000 if payload else None

                    # Construir los puntos a enviar (x: tiempo, y: vibración)
                    data_points = [
                        {"x": round(timestamp + i * sampling_period * step, 8), "y": value / 1000}
                        for i, value in enumerate(filtered)
                    ]

                    # Respuesta enviada al frontend
                    response = {
                        "sensor_id": current_sensor_id,
                        "source_timestamp": timestamp,
                        "sampling_period": sampling_period,
                        "original_points": total,
                        "downsampled_points": len(data_points),
                        "max_value": max_value ,
                        "min_value": min_value,
                        "data": data_points
                    }

                    await manager.send_json(websocket, response)

            # Si no hay nuevo documento, no se envía nada
            await asyncio.sleep(0.2)

    except errors.ServerSelectionTimeoutError as e:
        logging.error(f"{ErrorMessages.MONGO_TIMEOUT}: {str(e)}")
        await send_error(manager, websocket, ErrorMessages.MONGO_TIMEOUT, f"Error al consultar MongoDB: {str(e)}")
        sys.exit(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"Cliente desconectado: {client_ip}")
    except Exception as e:
        logging.error(f"{ErrorMessages.UNEXPECTED_ERROR} para cliente {client_ip}: {str(e)}")
        await send_error(manager, websocket, ErrorMessages.UNEXPECTED_ERROR, str(e))
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
