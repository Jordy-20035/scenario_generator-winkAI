# Пошаговая инструкция по установке

## Проблемы, которые были исправлены:
1. ✅ Версия natasha изменена с 1.6.1 на 1.6.0
2. ✅ Добавлена обработка ошибок для отсутствующих библиотек
3. ✅ Созданы скрипты для установки моделей

## Шаги установки:

### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

Это должно пройти успешно теперь, так как версия natasha исправлена.

### 2. Установите NLP модели

**Важно**: Модели нужно устанавливать ПОСЛЕ установки requirements.txt!

**Windows:**
```bash
install_models.bat
```

**Или вручную:**
```bash
python -m spacy download ru_core_news_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Создайте необходимые директории
```bash
mkdir uploads outputs
```

### 4. Запустите приложение

**Терминал 1 (Backend):**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Терминал 2 (Frontend):**
```bash
streamlit run frontend/app.py --server.port 8501
```

### 5. Откройте в браузере
- Streamlit: http://localhost:8501
- API docs: http://localhost:8000/docs

## Если возникают ошибки:

### Ошибка: "No module named 'spacy'"
Установите зависимости еще раз:
```bash
pip install -r requirements.txt
```

### Ошибка: "ru_core_news_sm not found"
Установите модель:
```bash
python -m spacy download ru_core_news_sm
```

### Ошибка: "natasha not available"
Это нормально! Код будет работать, но с ограниченным функционалом. 
Для полного функционала установите natasha:
```bash
pip install natasha==1.6.0
```

