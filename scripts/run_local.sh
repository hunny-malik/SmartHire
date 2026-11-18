#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

echo "=========================================================="
echo "             STARTING SMART HIRE SERVICES                "
echo "=========================================================="

echo "Starting Backend on http://localhost:8000..."
cd "$DIR/backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Frontend on http://localhost:5173..."
cd "$DIR/frontend" && npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
