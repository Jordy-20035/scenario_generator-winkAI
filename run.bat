@echo off
REM Windows batch script to run the application

echo Starting Scenario Pre-Production Generator...

REM Check if Docker is available
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo Using Docker...
    docker-compose up --build
) else (
    echo Docker not found. Running directly...
    
    REM Create necessary directories
    if not exist uploads mkdir uploads
    if not exist outputs mkdir outputs
    
    REM Check if virtual environment exists
    if not exist venv (
        echo Creating virtual environment...
        python -m venv venv
    )
    
    REM Activate virtual environment
    call venv\Scripts\activate.bat
    
    REM Install dependencies
    echo Installing dependencies...
    pip install -r requirements.txt
    
    REM Download models
    echo Downloading NLP models...
    python -m spacy download ru_core_news_sm
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
    
    REM Start backend in new window
    echo Starting FastAPI backend...
    start "FastAPI Backend" cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
    
    REM Wait a bit for backend to start
    timeout /t 3 /nobreak >nul
    
    REM Run frontend
    echo Starting Streamlit frontend...
    streamlit run frontend/app.py --server.port 8501
)

pause

