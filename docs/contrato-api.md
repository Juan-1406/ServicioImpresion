# Contrato de integración

Contrato indicado en el enunciado. Salvo `/health`, estos endpoints están pendientes de implementación.

| Método | Ruta | Solicitud | Respuesta |
| --- | --- | --- | --- |
| GET | `/health` | Sin cuerpo | 200, `{"status":"ok"}` (convención inicial del equipo) |
| POST | `/impresiones` | `{"codigo":"EP-A1B2C3D4"}` | 202, `{"trabajo_id":"job-123","estado":"PENDIENTE"}` |
| GET | `/impresiones/{trabajo_id}` | Sin cuerpo | 200, `{"trabajo_id":"job-123","codigo":"EP-A1B2C3D4","estado":"PENDIENTE"}` |
| POST | `/impresiones/siguiente` | Sin cuerpo | 200, trabajo reservado con código y estado `EN_PROCESO`; 204 sin cuerpo si no hay pendientes |
| POST | `/impresiones/{trabajo_id}/resultado` | `{"estado":"IMPRESO"}` o `{"estado":"ERROR"}` | 200, identificador y estado final |

Trabajo inexistente al consultar: HTTP 404 con `{"error":"TRABAJO_NO_EXISTE","mensaje":"Trabajo no encontrado"}`.

## Reglas

- Cada solicitud de creación obtiene un identificador único y comienza en `PENDIENTE`.
- La reserva elige un solo trabajo pendiente y lo cambia a `EN_PROCESO` en la misma sección protegida por un bloqueo.
- Solo un trabajo `EN_PROCESO` acepta un resultado `IMPRESO` o `ERROR`.
- Un trabajo reservado no vuelve a salir en consultas posteriores de la cola.
- Se permite almacenamiento en memoria y un solo agente. Reiniciar la API pierde la cola.
- Usar un solo proceso de API mientras la cola esté en memoria, para evitar colas independientes por proceso.

## Integraciones externas

El agente accede al Gateway mediante `API_BASE_URL`. Para obtener el ticket solicita `GET /api/tickets/{codigo}`, cuya respuesta esperada es una imagen PNG.

## Acuerdos pendientes

Confirmar con los equipos correspondientes los prefijos del Gateway, autenticación si corresponde y errores para transiciones inválidas. El enunciado no fija el código HTTP ni el cuerpo de esos errores.
