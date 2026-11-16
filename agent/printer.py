"""Impresión Windows mediante el controlador instalado y PrintDocument."""

import os
from pathlib import Path
import subprocess
import sys


def print_png(path: Path, printer_name: str):
    if sys.platform != "win32":
        raise RuntimeError("Este adaptador requiere Windows y una impresora instalada")
    env = os.environ.copy()
    env["EVENTPASS_PNG"] = str(path.resolve())
    env["EVENTPASS_PRINTER"] = printer_name
    # Los valores viajan por variables de entorno, nunca como código PowerShell.
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
         str(Path(__file__).with_name("print_ticket.ps1"))],
        env=env, capture_output=True, text=True, errors="replace", timeout=60,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode:
        raise RuntimeError(f"Falló la impresión: {result.stderr.strip()}")
