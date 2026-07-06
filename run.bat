@echo off
setlocal

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

start "ExamDigest Backend" cmd /k "uv run python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload"
start "ExamDigest Streamlit" cmd /k "uv run python -m streamlit run streamlit_app/app.py"

echo.
echo Backend: http://localhost:8000
echo UI: http://localhost:8501
echo.
echo Both services were started in separate terminals.
echo Press any key to exit this launcher.
pause >nul
