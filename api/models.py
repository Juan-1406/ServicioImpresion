from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Estado(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    IMPRESO = "IMPRESO"
    ERROR = "ERROR"


class CrearTrabajo(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    codigo: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


class Resultado(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: Literal["IMPRESO", "ERROR"]


class ResumenTrabajo(BaseModel):
    trabajo_id: str
    estado: Estado


class Trabajo(ResumenTrabajo):
    codigo: str
