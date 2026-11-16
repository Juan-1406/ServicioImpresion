import json
import logging
import os
from pathlib import Path
import tempfile
import time
from urllib.parse import urlparse

from dotenv import load_dotenv

from .client import GatewayClient
from .printer import print_png

log = logging.getLogger("eventpass.agent")


class Agent:
    def __init__(self, client, printer_name, state_file, printer=print_png):
        self.client = client
        self.printer_name = printer_name
        self.state_file = Path(state_file)
        self.printer = printer

    def save(self, state):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_file.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(state, file)
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(self.state_file)

    def flush_report(self):
        state = json.loads(self.state_file.read_text(encoding="utf-8"))
        if state["estado"] == "EN_PROCESO":
            # Tras un cierre inesperado el resultado físico es desconocido.
            # Nunca reenviar el ticket automáticamente.
            log.error("Trabajo interrumpido %s; se reportará ERROR para revisión manual",
                      state["trabajo_id"])
            state["estado"] = "ERROR"
            self.save(state)
        if state["estado"] not in ("IMPRESO", "ERROR"):
            raise ValueError("Registro local inválido; revisar antes de continuar")
        self.client.report(state["trabajo_id"], state["estado"])
        self.state_file.unlink()
        log.info("Resultado registrado: %s %s", state["trabajo_id"], state["estado"])

    def run_once(self):
        if self.state_file.exists():
            self.flush_report()
            return
        job = self.client.reserve()
        if job is None:
            return
        state = {"trabajo_id": job["trabajo_id"], "estado": "EN_PROCESO"}
        self.save(state)
        try:
            data = self.client.download(job["codigo"])
            with tempfile.TemporaryDirectory(prefix="eventpass-") as directory:
                path = Path(directory) / "ticket.png"
                path.write_bytes(data)
                self.printer(path, self.printer_name)
        except Exception:
            log.exception("Falló el trabajo %s", job["trabajo_id"])
            state["estado"] = "ERROR"
        else:
            state["estado"] = "IMPRESO"
        self.save(state)
        self.flush_report()


def main():
    load_dotenv(Path(__file__).with_name(".env"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    base_url = os.getenv("API_BASE_URL", "").strip()
    printer_name = os.getenv("PRINTER_NAME", "").strip()
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
        raise SystemExit("Configura API_BASE_URL con la URL del Gateway")
    if parsed.hostname and parsed.hostname.endswith(".invalid"):
        raise SystemExit("Reemplaza la URL de ejemplo por la URL real del Gateway")
    if not printer_name or printer_name == "COMPLETAR":
        raise SystemExit("Configura PRINTER_NAME con una impresora instalada")
    state_file = Path(os.getenv("AGENT_STATE_FILE", "agent-state.json"))
    if not state_file.is_absolute():
        state_file = Path(__file__).parent / state_file
    client = GatewayClient(base_url)
    agent = Agent(client, printer_name, state_file)
    try:
        while True:
            try:
                agent.run_once()
            except Exception:
                log.exception("No se pudo completar el ciclo; se reintentará sin reimprimir")
            time.sleep(2)
    except KeyboardInterrupt:
        log.info("Agente detenido")
    finally:
        client.close()


if __name__ == "__main__":
    main()
