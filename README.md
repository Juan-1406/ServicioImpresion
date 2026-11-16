# EventPass — Impresión térmica

Módulo del Equipo 08: API FastAPI para Railway y agente Python local para una impresora instalada en Windows. Requiere Python 3.10 o superior.

## Estructura

```text
api/
  main.py                 # Endpoints y errores
  models.py               # Solicitudes y estados
  job_queue.py            # Cola FIFO en memoria con bloqueo
  requirements.txt

agent/
  main.py                 # Consulta y recuperación de reportes
  client.py               # Gateway y validación del PNG
  printer.py              # Adaptador Windows
  print_ticket.ps1        # Impresión con PrintDocument
  .env.example
  requirements.txt

docs/
  secuencia.mmd

requirements-dev.txt
```

## Instalar y ejecutar la API

Desde la raíz del repositorio, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir api --reload
```


## Configurar y ejecutar el agente

En el computador Windows de la impresora, instalar `agent/requirements.txt` y preparar la configuración:

```powershell
Copy-Item agent/.env.example agent/.env
Get-Printer | Select-Object Name, PrinterStatus
```

Editar `agent/.env` con la URL real del Gateway y el nombre exacto de la impresora instalada. Para pruebas locales sin Gateway se puede usar `http://127.0.0.1:8000`, pero la descarga fallará hasta disponer de `/api/tickets/{codigo}`.

Desde la raíz, en una segunda terminal:

```powershell
.\.venv\Scripts\python.exe -m agent.main
```

Ejecutar una sola instancia del agente. Detener con Ctrl+C. Consulta cada dos segundos mediante conexiones salientes al Gateway.

El adaptador ejecuta su script PowerShell con `-ExecutionPolicy Bypass` solo para ese proceso; no modifica la política del equipo. Si una política institucional bloquea la ejecución, el trabajo quedará en `ERROR` y deberá revisarse con el encargado.

Configurar previamente el papel térmico en las preferencias del controlador. El PNG se ajusta manteniendo su proporción al área imprimible de una página. Verificar en la sala tamaño, márgenes y lectura del QR. El corte de papel específico de cada fabricante no está implementado.

`IMPRESO` significa que el controlador Windows aceptó el envío sin lanzar un error; no confirma la salida física del papel. Los errores de descarga y los detectados al enviar producen `ERROR`. Una impresora sin papel o desconectada puede mantener trabajos en la cola de Windows: revisar su estado durante la prueba presencial.

## Recuperación y límites

El agente guarda un registro local antes de imprimir y conserva el resultado hasta que la API lo confirma. Si falla el reporte, lo reintenta sin volver a imprimir. Si reinicia con un trabajo interrumpido, reporta `ERROR` para revisión manual: pudo haberse enviado físicamente antes de la interrupción. No borrar el registro para forzar reimpresiones.

Si la API reinicia y pierde un trabajo cuyo reporte quedó pendiente, el agente conserva ese reporte y no toma otros trabajos. Detenerlo y revisar `agent/agent-state.json` con el encargado antes de archivarlo o retirarlo. Una respuesta perdida durante la reserva puede dejar un trabajo `EN_PROCESO`; el contrato no ofrece recuperación de reservas ni garantiza impresión exactamente una vez frente a caídas. No se reencola automáticamente.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest api/tests agent/tests -q
```

Cubren contrato HTTP, FIFO, reservas concurrentes, transiciones inválidas, descargas y fallos de impresión, y recuperación del reporte. La prueba de integración usa API y cliente HTTP reales con Gateway, tickets e impresora simulados. No envía papel.

## Entrega

Completar la solicitud de `docs/despliegue.md`. Solo la API va en Railway. Confirmar con los otros equipos las rutas del Gateway, el PNG y la impresora. El diagrama requerido está en `docs/secuencia.mmd`.

Referencias: [pruebas FastAPI](https://fastapi.tiangolo.com/tutorial/testing/) y [PrintDocument de Microsoft](https://learn.microsoft.com/dotnet/api/system.drawing.printing.printdocument).
