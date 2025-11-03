#!/bin/bash
# Script to install NLP models after requirements are installed

echo "Installing NLP models..."

echo ""
echo "Step 1: Installing spaCy Russian model..."
python -m spacy download ru_core_news_sm

echo ""
echo "Step 2: Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo ""
echo "Done! Models are installed."

