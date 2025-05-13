#!/bin/bash

# Number of clients to start
NUM_CLIENTS=25

# Start the server in the background
echo "[SCRIPT] Starting server..."
python3 server.py &
SERVER_PID=$!
echo "[SCRIPT] Server running with PID $SERVER_PID"

trap "echo '[SCRIPT] Ctrl+C detected. Killing server...'; kill $SERVER_PID; exit 1" SIGINT

# Give the server a moment to start
sleep 1

# Start clients in the background
echo "[SCRIPT] Starting $NUM_CLIENTS clients..."
for ((i=1; i<=NUM_CLIENTS; i++)); do
    python3 client.py arquivo_1mb &
done

# Wait for all clients to finish
wait
echo "[SCRIPT] All clients finished."

# Stop the server
echo "[SCRIPT] Stopping server (PID $SERVER_PID)..."
kill $SERVER_PID

echo "[SCRIPT] Done."
