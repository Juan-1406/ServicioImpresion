# Solicitud de despliegue al docente

Completar y enviar cuando la API de trabajos esté implementada y probada.

- Repositorio: PENDIENTE de crear en la plataforma Git del equipo.
- Carpeta raíz del servicio: `api`.
- Dependencias: `api/requirements.txt`.
- Comando de instalación desde esa carpeta: `pip install -r requirements.txt`.
- Comando de inicio: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Comprobación de salud: `GET /health`.
- Procesos: uno, sin múltiples workers, porque la cola reside en memoria.

Desplegar únicamente la API en Railway. El agente se ejecuta en el computador conectado a la impresora y realiza conexiones salientes al Gateway; no necesita puertos locales públicos.

Solicitar al docente la URL pública del Gateway y confirmar el enrutamiento de `/impresiones` y `/api/tickets/{codigo}`. Configurar esa URL en `agent/.env` mediante `API_BASE_URL`.

La cola se pierde al reiniciar la API, según lo permitido por el enunciado.
