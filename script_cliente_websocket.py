import asyncio
import websockets
import json

API_URL = "ws://localhost:8000/vibraciones"  # Cambia localhost si tu API está en otro host
SENSOR_ID = 32417

async def recibir_datos():
    async with websockets.connect(API_URL) as websocket:
        # Enviar el sensor_id al conectar
        await websocket.send(json.dumps({"sensor_id": SENSOR_ID}))

        while True:
            try:
                mensaje = await websocket.recv()
                datos = json.loads(mensaje)

                puntos = datos.get("data", [])
                if puntos:
                    print("Primer punto recibido:", puntos[0])
                else:
                    print("Sin datos")

            except Exception as e:
                print(f"❌ Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(recibir_datos())
