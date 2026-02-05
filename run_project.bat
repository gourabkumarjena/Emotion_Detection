@echo off
echo Starting Emotion Detector Project...

echo Starting Backend...
start "Emotion Detector Backend" cmd /k "venv\Scripts\activate && cd backend && python main.py"

echo Starting Frontend...
start "Emotion Detector Frontend" cmd /k "cd frontend && npm run dev"

echo Project Started!
echo Backend running at http://localhost:8000
echo Frontend running at http://localhost:5173
echo Press any key to exit this launcher (terminals will remain open)...
pause
