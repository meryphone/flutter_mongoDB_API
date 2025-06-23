import os
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from typing import List
from fastapi.responses import JSONResponse
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cargar variables de entorno
load_dotenv()

# Inicializar la app
app = FastAPI()

# Quitar para pasar a produccion
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enum de errores
class ErrorMessages(str, Enum):
    DATA_NOT_FOUND = "Datos no encontrados"
    UNEXPECTED_ERROR = "Error inesperado"

DESIRED_POINTS = 1000 

# Conexión MongoDB
MONGO_URI = os.getenv("MONGO_URI")
try:
    mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo["vibraciones"]
    collection = db["paquetes"]
    if collection is None:
        logging.error("La colección 'paquetes' no se pudo obtener.")
        raise RuntimeError("La colección 'paquetes' no se pudo obtener.")
except errors.ServerSelectionTimeoutError as e:
    logging.error("Error de tiempo de espera al conectar con MongoDB: %s", e)
    collection = None

def check_mongo_connection():
    try:
        mongo.admin.command("ping")
        return True
    except Exception as e:
        logging.warning("MongoDB ping failed: %s", e) # PONER LOGS PARA PASAR A PRODUCCION
        return False

@app.get("/")
def home():
    mongo_status = "connected" if check_mongo_connection() else "disconnected"
    status = {
        "api_status": "ok",
        "mongodb_status": mongo_status
    }
    return JSONResponse(content=status)

@app.get("/vibraciones/{sensor_id}")
def obtener_vibracion(sensor_id: int):

    allowed_sensor_ids = [32417, 32416, 32418, 32419]  
    if sensor_id not in allowed_sensor_ids:
        logging.warning(f"sensor_id {sensor_id} no está en la lista de valores permitidos")
        raise HTTPException(status_code=400, detail="sensor_id no permitido")

    try:
        logging.info(f"Consultando MongoDB para sensor_id: {sensor_id}")
        doc = collection.find_one({"id": sensor_id}, sort=[("timestamp", -1)])
        if not doc:
            logging.warning(f"No se encontraron datos para sensor_id {sensor_id}")
            raise HTTPException(status_code=404, detail=ErrorMessages.DATA_NOT_FOUND)

        payload = doc["payload_values"]
        sampling_period = doc["sampl_period"]
        timestamp = doc["timestamp"]

        total = len(payload)
        step = max(1, total // DESIRED_POINTS)
        filtered = payload[::step]

        data_points = []
        for i, value in enumerate(filtered):
            x = round(timestamp + i * sampling_period * step, 8)
            data_points.append({"x": x, "y": value})
        
        response = {
            "sensor_id": sensor_id,
            "source_timestamp": timestamp,
            "sampling_period": sampling_period,
            "original_points": total,
            "downsampled_points": len(data_points),
            "data": data_points
        }

        logging.info(f"Datos enviados para sensor_id {sensor_id}")
        return JSONResponse(status_code=200, content=response)

    except Exception as e:
        logging.error(f"Error inesperado en la consulta: {str(e)}")
        raise HTTPException(status_code=500, detail=ErrorMessages.UNEXPECTED_ERROR)

@app.get("/vibraciones")
async def get_vibraciones(sensor_id: int):
    """
    Endpoint HTTP GET que recibe el sensor_id como parámetro de la URL (?sensor_id=32417)
    y devuelve los datos del sensor.
    """
    try:
        doc = collection.find_one({"id": int(sensor_id)}, sort=[("timestamp", -1)])
        if not doc:
            return JSONResponse(
                status_code=404,
                content={"error": ErrorMessages.DATA_NOT_FOUND, "details": f"No se encontraron datos para sensor_id {sensor_id}"}
            )

        timestamp = doc["timestamp"]
        payload = doc["payload_values"]
        sampling_period = doc["sampl_period"]

        total = len(payload)
        step = max(1, total // DESIRED_POINTS)
        filtered = payload[::step]

        data_points = [
            {"x": round(timestamp + i * sampling_period * step, 8), "y": value / DESIRED_POINTS}
            for i, value in enumerate(filtered)
        ]

        response = {
            "sensor_id": sensor_id,
            "source_timestamp": timestamp,
            "sampling_period": sampling_period,
            "original_points": total,
            "downsampled_points": len(data_points),
            "data": data_points
        }
        
        print(f"Timestamp enviado: {timestamp}")

        return JSONResponse(content=response)
    except Exception as e:
        logging.error(f"Error inesperado en la consulta: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": ErrorMessages.UNEXPECTED_ERROR, "details": str(e)}
        )

if __name__ == "__main__":
     uvicorn.run(app, host="0.0.0.0", port=8000)
