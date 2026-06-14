# Task 05 — Minimal REST endpoint
## Category: web-server
## Language: python
## Requirement
Create `server.py` exposing a WSGI `app(environ, start_response)` (PEP 3333) that handles
`GET /health` → `200` with JSON body `{"status": "ok"}`, and any other path → `404`. It must be
runnable with `wsgiref.simple_server` without any third-party web framework.
## Done when
- `test_server.py` exists and passes under `pytest`, calling `app` directly (or via
  `wsgiref.test` helpers) without binding a real socket.
- `GET /health` returns status 200 and a body that parses to `{"status": "ok"}`.
- `GET /nope` returns status 404.
