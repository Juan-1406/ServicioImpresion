from io import BytesIO
from urllib.parse import quote

import httpx
from PIL import Image

MAX_PNG_BYTES = 10 * 1024 * 1024


class GatewayClient:
    def __init__(self, base_url: str, transport=None):
        self.http = httpx.Client(base_url=base_url.rstrip("/") + "/",
                                 timeout=15, transport=transport)

    def close(self):
        self.http.close()

    def reserve(self) -> dict | None:
        # No reintentar este POST automáticamente: una respuesta perdida puede
        # corresponder a una reserva que ya se confirmó en el servidor.
        response = self.http.post("impresiones/siguiente")
        if response.status_code == 204:
            return None
        response.raise_for_status()
        job = response.json()
        if (job.get("estado") != "EN_PROCESO" or not isinstance(job.get("codigo"), str)
                or not isinstance(job.get("trabajo_id"), str)):
            raise ValueError("Respuesta de reserva inválida")
        return job

    def download(self, codigo: str) -> bytes:
        with self.http.stream("GET", f"api/tickets/{quote(codigo, safe='')}") as response:
            response.raise_for_status()
            data = bytearray()
            for chunk in response.iter_bytes():
                data.extend(chunk)
                if len(data) > MAX_PNG_BYTES:
                    raise ValueError("El ticket supera el máximo de 10 MB")
        raw = bytes(data)
        with Image.open(BytesIO(raw)) as image:
            if image.format != "PNG":
                raise ValueError("El ticket no es un PNG")
            if image.width * image.height > 20_000_000:
                raise ValueError("Las dimensiones del ticket son excesivas")
            image.verify()
        return raw

    def report(self, job_id: str, estado: str):
        path = f"impresiones/{quote(job_id, safe='')}/resultado"
        response = self.http.post(path, json={"estado": estado})
        # Una respuesta de éxito perdida puede producir 409 al repetir el reporte.
        # Consultar permite confirmar el mismo resultado sin repetir la impresión.
        if response.status_code == 409:
            current = self.http.get(f"impresiones/{quote(job_id, safe='')}")
            current.raise_for_status()
            if current.json().get("estado") == estado:
                return
        response.raise_for_status()
        confirmed = response.json()
        if confirmed.get("trabajo_id") != job_id or confirmed.get("estado") != estado:
            raise ValueError("El Gateway no confirmó el resultado del trabajo")
