
import os
import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Cargar variables de entorno
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Inicializar MongoDB
client = MongoClient(MONGO_URI)
collection = client["vibraciones"]["test"]

# Inicializar FastAPIs
app = FastAPI()

# Parámetros
DESIRED_POINTS = 500

@app.websocket("/vibraciones")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    sensor_id = None
    last_doc_id = None

    try:
        # Recibir sensor_id inicial
        msg = await websocket.receive_json()
        sensor_id = int(msg.get("sensor_id", 0))

        while True:
            # Buscar el último documento
            doc = collection.find_one({"id": sensor_id}, sort=[("timestamp", -1)])
            if doc and doc["_id"] != last_doc_id:
                last_doc_id = doc["_id"]
                payload = doc["payload_values"]
                sampling_period = doc["sampl_period"]
                timestamp = doc["timestamp"]

                # Downsampling
                total = len(payload)
                step = max(1, total // DESIRED_POINTS)
                data = [
                    {"x": round(timestamp + i * sampling_period * step, 8), "y": val }
                    for i, val in enumerate(payload[::step])
                ]

                print(f"Timestamp enviado: {timestamp}")

                # Enviar al cliente
                await websocket.send_text(json.dumps({
                    "sensor_id": sensor_id,
                    "source_timestamp": timestamp,
                    "sampling_period": sampling_period,
                    "original_points": total,
                    "downsampled_points": len(data),
                    "data": data
                }))

            await asyncio.sleep(0.2)

    except Exception as e:
        logging.error(f"Error en conexión WebSocket: {e}")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
