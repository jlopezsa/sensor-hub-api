Param(
    [int]$Port = 8000
)

if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Error "Poetry no está instalado. Instálalo: https://python-poetry.org/docs/"
    exit 1
}

poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port $Port

