@echo off
"%~dp0.venv\Scripts\python.exe" -m alembic upgrade head
if errorlevel 1 exit /b %errorlevel%

"%~dp0.venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
