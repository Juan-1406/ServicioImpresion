"""Cola FIFO en memoria. Un único proceso de servidor comparte este bloqueo."""

from collections import deque
from threading import Lock
from uuid import uuid4

try:
    from .models import Estado, Trabajo
except ImportError:  # uvicorn main:app desde la carpeta api
    from models import Estado, Trabajo


class TrabajoNoExiste(Exception):
    pass


class EstadoInvalido(Exception):
    pass


class JobQueue:
    def __init__(self):
        self._lock = Lock()
        self._jobs: dict[str, Trabajo] = {}
        self._pending: deque[str] = deque()

    def create(self, codigo: str) -> Trabajo:
        with self._lock:
            job = Trabajo(trabajo_id=f"job-{uuid4()}", codigo=codigo, estado=Estado.PENDIENTE)
            self._jobs[job.trabajo_id] = job
            self._pending.append(job.trabajo_id)
            return job.model_copy()

    def get(self, job_id: str) -> Trabajo:
        with self._lock:
            if job_id not in self._jobs:
                raise TrabajoNoExiste()
            return self._jobs[job_id].model_copy()

    def reserve(self) -> Trabajo | None:
        with self._lock:
            if not self._pending:
                return None
            job = self._jobs[self._pending.popleft()]
            job.estado = Estado.EN_PROCESO
            return job.model_copy()

    def finish(self, job_id: str, estado: str) -> Trabajo:
        with self._lock:
            if job_id not in self._jobs:
                raise TrabajoNoExiste()
            job = self._jobs[job_id]
            if job.estado != Estado.EN_PROCESO or estado not in ("IMPRESO", "ERROR"):
                raise EstadoInvalido()
            job.estado = Estado(estado)
            return job.model_copy()
