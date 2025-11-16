FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# spaCy model (pinned)
RUN pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/ru_core_news_sm-3.7.0/ru_core_news_sm-3.7.0-py3-none-any.whl

# NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

COPY . .

EXPOSE 8000 8501

CMD ["bash","-lc","uvicorn backend.main:app --host 0.0.0.0 --port 8000 & \
      streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]

