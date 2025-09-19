@echo off
echo Starting POWERGRID AI Ticketing System...

echo Starting Backend...
start cmd /k "cd backend && python -m src.main"

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo System started! Access the application at http://localhost:5173