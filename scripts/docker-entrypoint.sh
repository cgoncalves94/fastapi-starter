#!/usr/bin/env bash

# Exit if any command fails
set -e

# Set project root
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT="$SCRIPT_DIR/.."

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head
echo "Migrations complete."

# Application path for FastAPI CLI
APP_PATH="src/app/main.py"

# Set host and port
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8000}

# Start FastAPI development server
echo "Starting FastAPI development server on $HOST:$PORT..."
cd "$PROJECT_ROOT" && exec fastapi dev "$APP_PATH" --host "$HOST" --port "$PORT"
