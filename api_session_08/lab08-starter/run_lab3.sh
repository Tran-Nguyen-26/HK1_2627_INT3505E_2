#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Ensure Node/Newman are on PATH
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    export NVM_DIR="$HOME/.nvm"
    \. "$NVM_DIR/nvm.sh"
    nvm use 20 >/dev/null 2>&1 || true
fi
export PATH="/home/ttn/.gemini/antigravity/bin:$DIR/.venv/bin:$HOME/lab08_venv/bin:$PATH"

# Choose Python
if [ -x "$DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$DIR/.venv/bin/python"
elif [ -x "$HOME/lab08_venv/bin/python" ]; then
    PYTHON_CMD="$HOME/lab08_venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Check if Flask server is already running on port 5000
SERVER_PID=""
if ! curl -s "http://127.0.0.1:5000/health" > /dev/null 2>&1; then
    echo "Starting Flask API in background..."
    PYTHONPATH=. "$PYTHON_CMD" -m app --port 5000 > /dev/null 2>&1 &
    SERVER_PID=$!
    # Wait until server is up
    for i in {1..30}; do
        if curl -s "http://127.0.0.1:5000/health" > /dev/null 2>&1; then
            echo "Flask API is up and ready."
            break
        fi
        sleep 0.2
    done
else
    echo "Flask API is already running on port 5000."
fi

cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping background Flask API (PID $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Environment file: prefer staging.postman_environment.json if present, else postman/local.postman_environment.json
ENV_FILE="staging.postman_environment.json"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="postman/local.postman_environment.json"
fi

mkdir -p reports

echo "Running Newman test suite..."
newman run books-api.postman_collection.json \
  -e "$ENV_FILE" \
  -r cli,junit \
  --reporter-junit-export junit.xml

# Also mirror junit.xml into reports/
cp junit.xml reports/junit.xml 2>/dev/null || true

echo "Done! JUnit report saved to junit.xml and reports/junit.xml"
