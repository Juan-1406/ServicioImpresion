"""Entrada de la API de impresión. La cola se implementará en una etapa posterior."""

from fastapi import FastAPI

app = FastAPI(title="EventPass - Impresión térmica")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
