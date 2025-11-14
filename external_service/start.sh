#!/bin/bash
set -euo pipefail

# Ensure child processes stop when the container stops
cleanup() {
  if [[ -n "${UVICORN_PID:-}" ]]; then
    kill -TERM "$UVICORN_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

# Start HTTP/1.1 endpoint on 8001 for baseline tests
uvicorn main:app --host 0.0.0.0 --port 8001 &
UVICORN_PID=$!

# Start HTTPS/HTTP2 endpoint on 8443 using Hypercorn
hypercorn main:app \
  --bind 0.0.0.0:8443 \
  --certfile certs/external_service.crt \
  --keyfile certs/external_service.key

wait $UVICORN_PID
