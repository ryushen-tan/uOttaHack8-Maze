DIR=".env"

if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v proj &> /dev/null; then
        echo "Detected macOS with missing PROJ library."
        if command -v brew &> /dev/null; then
            echo "Attempting to install 'proj' via Homebrew..."
            brew install proj
        else
            echo "WARNING: 'proj' library is missing and Homebrew was not found."
            echo "If the installation fails, please install Homebrew and run: brew install proj"
        fi
    fi
fi

if [ ! -d "$DIR" ]; then
  echo "Creating virtual environment..."
  if command -v python3 &>/dev/null; then
    python3 -m venv "$DIR"
  else
    python -m venv "$DIR"
  fi
fi

if [ -f "$DIR/bin/activate" ]; then
    source "$DIR/bin/activate"
elif [ -f "$DIR/Scripts/activate" ]; then
    source "$DIR/Scripts/activate"
fi

pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found."
fi