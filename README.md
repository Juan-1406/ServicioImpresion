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

Ejecutar una sola instancia del agente. Consulta cada dos segundos mediante conexiones salientes al Gateway.

`IMPRESO` significa que el controlador Windows aceptó el envío sin lanzar un error; no confirma la salida física del papel. Los errores de descarga y los detectados al enviar producen `ERROR`.