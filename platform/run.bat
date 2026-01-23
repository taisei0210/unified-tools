@echo off
cd /d %~dp0
call venv\Scripts\activate
echo Starting Vibe Tools Platform...
start http://localhost:8001
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8001
pause
