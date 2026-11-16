from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

try:
    from .job_queue import EstadoInvalido, JobQueue, TrabajoNoExiste
    from .models import CrearTrabajo, Resultado, ResumenTrabajo, Trabajo
except ImportError:
    from job_queue import EstadoInvalido, JobQueue, TrabajoNoExiste
    from models import CrearTrabajo, Resultado, ResumenTrabajo, Trabajo


def create_app() -> FastAPI:
    app = FastAPI(title="EventPass - Impresión térmica", version="1.0.0")
    queue = JobQueue()

    @app.exception_handler(TrabajoNoExiste)
    async def missing(_request, _exc):
        return JSONResponse(status_code=404, content={
            "error": "TRABAJO_NO_EXISTE", "mensaje": "Trabajo no encontrado"
        })

    @app.exception_handler(EstadoInvalido)
    async def invalid(_request, _exc):
        return JSONResponse(status_code=409, content={
            "error": "ESTADO_INVALIDO", "mensaje": "El trabajo debe estar EN_PROCESO"
        })

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/impresiones", status_code=202, response_model=ResumenTrabajo)
    def create(body: CrearTrabajo):
        return queue.create(body.codigo)

    @app.post("/impresiones/siguiente", response_model=Trabajo,
              responses={204: {"description": "Sin trabajos pendientes"}})
    def reserve():
        job = queue.reserve()
        return job if job is not None else Response(status_code=204)

    @app.get("/impresiones/{trabajo_id}", response_model=Trabajo)
    def get(trabajo_id: str):
        return queue.get(trabajo_id)

    @app.post("/impresiones/{trabajo_id}/resultado", response_model=ResumenTrabajo)
    def finish(trabajo_id: str, body: Resultado):
        return queue.finish(trabajo_id, body.estado)

    return app


app = create_app()