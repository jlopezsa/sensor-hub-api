#!/usr/bin/env bash
set -e

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry no está instalado. Instálalo: https://python-poetry.org/docs/" >&2
  exit 1
fi

poetry install
exec poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

