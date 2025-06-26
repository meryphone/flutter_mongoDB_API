# Monitor de Vibraciones en Tiempo Real

Este proyecto permite la visualización en tiempo real de datos de vibración obtenidos desde sensores, utilizando una arquitectura moderna basada en:

- FastAPI + WebSocket para servir los datos desde MongoDB
- Flutter Web (generado con FlutterFlow) para el frontend interactivo
- Syncfusion Charts para representación gráfica fluida y dinámica

---

## Funcionalidades

- Conexión en tiempo real vía WebSocket
- Elección de sensor desde el frontend
- Actualización automática y continua de la gráfica
- Downsampling eficiente (hasta 500 puntos)
- Estadísticas instantáneas: valor mínimo y máximo de cada bloque
- Visualización directa desde el mismo backend (FastAPI sirve también el frontend)

---
