# Установка и запуск

## Способ 1: Docker (рекомендуется)

Самый простой способ запустить приложение:

```bash
docker-compose up --build
```

Приложение будет доступно:
- Streamlit: http://localhost:8501
- FastAPI API: http://localhost:8000
- API документация: http://localhost:8000/docs

## Способ 2: Локальная установка

### Требования
- Python 3.11+
- pip

### Шаги установки

1. **Клонируйте репозиторий** (если еще не сделано):
```bash
git clone <repository-url>
cd scenario_generator-winkAI-1
```

2. **Создайте виртуальное окружение**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

4. **Загрузите NLP модели**:
```bash
# spaCy русская модель
python -m spacy download ru_core_news_sm

# NLTK данные
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. **Создайте необходимые директории**:
```bash
mkdir uploads outputs
```

6. **Запустите приложение**:

**Вариант A: Использование скриптов**
- Windows: `run.bat`
- Linux/Mac: `chmod +x run.sh && ./run.sh`

**Вариант B: Ручной запуск**

Терминал 1 (Backend):
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Терминал 2 (Frontend):
```bash
streamlit run frontend/app.py --server.port 8501
```

## Проверка установки

1. Откройте http://localhost:8501 в браузере
2. Должен открыться интерфейс Streamlit
3. Проверьте API: http://localhost:8000/docs

## Решение проблем

### Проблема: Модель spaCy не найдена
```bash
python -m spacy download ru_core_news_sm
```

### Проблема: Порт уже занят
Измените порты в:
- `backend/main.py` (для FastAPI)
- `frontend/app.py` (для Streamlit)
- `docker-compose.yml` (для Docker)

### Проблема: Ошибки зависимостей
Убедитесь, что используется Python 3.11+:
```bash
python --version
```

Если версия меньше, обновите Python или используйте Docker.

### Проблема: Docker не запускается
Убедитесь, что:
1. Docker Desktop запущен
2. Порты 8000 и 8501 свободны
3. Docker имеет достаточно ресурсов (минимум 4GB RAM)

## Тестирование

После установки попробуйте загрузить тестовый сценарий:
1. Подготовьте файл PDF или DOCX со сценарием
2. Загрузите его через интерфейс
3. Проверьте результаты извлечения

