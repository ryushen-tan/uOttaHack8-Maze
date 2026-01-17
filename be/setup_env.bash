DIR=".env"

if [ ! -d "$DIR" ]; then
  python -m venv "$DIR"
fi

./$DIR/Scripts/activate

pip install -r requirements.txt