# Plan de desarrollo

## 1. API y cola

- Definir modelos y estados en `api/models.py`.
- Implementar almacenamiento y bloqueo en `api/queue.py`.
- Agregar los endpoints del contrato en `api/main.py`.
- Verificar creación, consulta inexistente, cola vacía, reserva única incluso con solicitudes concurrentes y rechazo de resultados fuera de `EN_PROCESO`.

## 2. Agente local

- Cargar `API_BASE_URL` y `PRINTER_NAME`; validar su configuración al iniciar.
- Implementar HTTP con tiempos de espera y manejo de errores en `agent/client.py`.
- Consultar cada dos segundos y tratar HTTP 204 como cola vacía.
- Descargar y validar el PNG antes de imprimir.
- Implementar `agent/printer.py` con el sistema operativo y la impresora confirmados.
- Reportar `ERROR` ante fallos de descarga o impresión; reportar `IMPRESO` solo cuando el mecanismo real de impresión confirme el envío correcto.
- Si falla el reporte tras enviar a la impresora, reintentar el reporte sin volver a imprimir. Definir este comportamiento antes de implementar reintentos.

## 3. Integración y entrega

- Probar con el Gateway y el servicio de tickets del curso.
- Probar éxito y fallo con la impresora del computador de la sala.
- Verificar que consultar repetidamente la cola no repite el mismo trabajo.
- Actualizar el diagrama si cambia el flujo acordado.
- Completar la solicitud de despliegue al docente y entregar el enlace Git.

## Información por confirmar

- URL pública y rutas del Gateway.
- Disponibilidad del endpoint PNG del servicio de tickets.
- Sistema operativo, modelo, controlador y nombre de la impresora instalada.
- Ancho del papel y dimensiones de la imagen del ticket.

La aceptación física del papel no siempre puede comprobarse desde el sistema operativo. Documentar qué confirma el controlador elegido y cómo se verificará la prueba presencial.
