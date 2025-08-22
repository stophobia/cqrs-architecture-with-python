#!/bin/bash

export ENVIRONMENT=${ENVIRONMENT:-development}
export PORT=${PORT:-8000}
export WORKERS=${WORKERS:-1}
export LOG_LEVEL=${LOG_LEVEL:-info}
export TIMEOUT=${TIMEOUT:-120}

echo "Rodando o servidor ($ENVIRONMENT)"

UVICORN_CMD=(
  uvicorn src.app:create_app --factory
  --host 0.0.0.0
  --port "$PORT"
  --log-level "$LOG_LEVEL"
)

# Ativa reload somente em dev
if [ "$ENVIRONMENT" = "development" ]; then
  UVICORN_CMD+=(--reload)
fi

# Usa exec pra receber sinais corretamente
exec "${UVICORN_CMD[@]}"
