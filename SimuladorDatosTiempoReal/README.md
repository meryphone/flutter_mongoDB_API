# Simulaciones de Envío y Recepción de Datos de Vibración

Este submódulo del proyecto permite simular el envío y la recepción de datos de sensores de vibración en tiempo real a través de sockets TCP, almacenándolos en MongoDB y sirviéndolos vía WebSocket.

---

## Archivos incluidos

### `envio_datos.py`
- Simula un sensor de vibraciones.
- Genera datos con distribución normal.
- Los empaqueta en formato binario (cabecera + payload).
- Envía los datos al servidor TCP cada segundo.

**Editar antes de usar:** 
- Cambiar `SERVER_IP` por la IP del servidor que ejecuta `insercion_datos.py`.

**Ejecutar:**
```bash
python envio_datos.py
```

---

### `insercion_datos.py`
- Actúa como servidor TCP receptor.
- Escucha en el puerto 8085.
- Recibe datos binarios, los parsea y guarda en MongoDB.
- Compatible con múltiples sensores.

**Ejecutar:**
```bash
python insercion_datos.py
```

---

## Flujo de funcionamiento

```plaintext
[envio_datos.py] --> TCP --> [insercion_datos.py] --> MongoDB --> [API FastAPI/WebSocket]
```

---

## Requisitos

- Python 3.10+
- MongoDB activo
- Paquetes Python:
  - `pymongo`
  - `struct`
  - `socket`

Instalación recomendada:

```bash
pip install pymongo
```

---

## Uso en pruebas

Útil para:
- Probar la visualización de datos sin hardware físico
- Validar la estructura de documentos en MongoDB
- Verificar el comportamiento del frontend ante entrada continua o pausada de datos

---


