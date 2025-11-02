# Быстрое исправление проблемы с импортами

## Проблема
При запуске из директории `backend` возникала ошибка `ModuleNotFoundError: No module named 'backend'`

## Решение
**Важно**: Запускать нужно из **корневой директории проекта**, а не из `backend`!

## Правильный порядок запуска:

### 1. Убедитесь, что вы в корневой директории проекта:
```bash
cd C:\Users\johnd\Downloads\projects\scenario_generator-winkAI-1
```

### 2. Запустите backend (из корневой директории):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 3. В другом терминале запустите frontend (тоже из корневой директории):
```bash
cd C:\Users\johnd\Downloads\projects\scenario_generator-winkAI-1
streamlit run frontend/app.py --server.port 8501
```

## Почему это важно?
- Импорты в `backend/main.py` используют `from backend.xxx import ...`
- Python должен видеть структуру проекта как пакет
- При запуске из корня проекта, Python правильно находит модули

## Альтернатива (если нужно запускать из backend):
Если по каким-то причинам нужно запускать из `backend`, можно изменить импорты на относительные, но это не рекомендуется.

