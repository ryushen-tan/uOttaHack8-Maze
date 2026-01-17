$path = ".venv"

if (-not (Test-Path $path)) {
    & python -m venv $path
}

& "$path/Scripts/activate"

pip install -r requirements.txt