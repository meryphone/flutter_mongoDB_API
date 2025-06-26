
![logodimensionao](https://github.com/user-attachments/assets/b94671bc-590d-4a23-a755-892ca98955e2)


# Monitor de Vibraciones en Tiempo Real
Este proyecto permite la visualización en tiempo real de datos de vibración almacenados en una base de datos MongoDB obtenidos desde distintos sensores, utilizando una arquitectura moderna basada en:

- FastAPI + WebSocket para servir los datos desde MongoDB
- Flutter Web (generado con FlutterFlow) para el frontend interactivo
- Syncfusion Charts para representación gráfica fluida y dinámica

---

## Funcionalidades

- Conexión en tiempo real vía WebSocket a la API
- Selección dinámica del sensor desde un desplegable en la UI
- Representación en vivo de los datos a medida que llegan (tipo Live Chart)
- Downsampling eficiente para mejorar rendimiento (hasta 500 puntos por lote)
- Visualización estadística del **valor mínimo y máximo** de vibración registrado.

---

## Comportamiento del sistema

- **Hay datos recientes** en MongoDB para el sensor seleccionado:
  - Se realiza un submuestreo del payload (`payload_values`)
  - La gráfica se actualiza automáticamente y de forma fluida
  - Se calculan y muestran el valor mínimo y máximo del bloque

- **No hay datos recientes**:
  - La gráfica muestra un mensaje: *"Esperando datos en tiempo real..."*
  - No se actualiza hasta que llegue un nuevo paquete

- **No hay datos para el sensor seleccionado**:
  - Se muestra un mensaje de error que indica que el sensor no tiene datos asociados
  - El sistema permite cambiar de sensor sin reiniciar

- **Cambio de sensor**:
  - El usuario puede cambiar el sensor en cualquier momento desde el desplegable
  - Se envía un nuevo `sensor_id` al WebSocket y se reinicia la gráfica con datos nuevos

- **Pausa visual**:
  - Se puede detener la representación de los datos en vivo para visualizar un momento en concreto mientras se estén recibiendo datos.
  - Se puede reanudar en cualquier momento y la grafica mostrará los datos mas recientes recibidos.

---

##  Ejecución del proyecto

Sigue estos pasos para instalar, configurar y ejecutar el sistema completo.

---

### 1. Clona el repositorio

```bash
git clone https://github.com/tu_usuario/monitor-vibraciones.git
cd monitor-vibraciones```
```

### 2. Crea un entorno virtaul (recomendado)

```bash
`python -m venv venv`
`source venv/bin/activate`  # En Linux/macOS
`venv\Scripts\activate`     # En Windows
```
### 4. Instala dependencias.

Instala las dependencias del fichero 

```bash 
pip install -r requirements.txt`
``` 
### 5. Crea las variables de entorno

Contenido de ejemplo del fichero .env de ejemplo:

```bash 
# URI de conexión a tu instancia de MongoDB
MONGO_URI=mongodb://usuario:contraseña@localhost:27017/vibraciones
```


