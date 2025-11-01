#!/bin/bash

# Script to run the application

echo "Starting Scenario Pre-Production Generator..."

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Using Docker..."
    docker-compose up --build
else
    echo "Docker not found. Running directly..."
    
    # Create necessary directories
    mkdir -p uploads outputs
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Download models
    echo "Downloading NLP models..."
    python -m spacy download ru_core_news_sm
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
    
    # Run backend in background
    echo "Starting FastAPI backend..."
    cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a bit for backend to start
    sleep 3
    
    # Run frontend
    echo "Starting Streamlit frontend..."
    streamlit run frontend/app.py --server.port 8501
    
    # Cleanup on exit
    kill $BACKEND_PID
fi

