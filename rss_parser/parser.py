import feedparser
import re
from collections import Counter
from typing import Dict, Generator, List
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import logging

def setup_nltk():
    """Загрузка ресурсов NLTK"""
    try:
        nltk.data.find('corpora/wordnet')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/omw-1.4')
    except nltk.downloader.DownloadError:
        logging.info("Скачиваем ресурсы NLTK...")
        nltk.download('wordnet')
        nltk.download('stopwords')
        nltk.download('omw-1.4')

# --- Генератор для парсинга RSS-ленты из текста ---
def parse_rss_feed_from_text(text: str) -> Generator[Dict, None, None]:
    feed = feedparser.parse(text)
    for entry in feed.entries:
        yield {
            'title': entry.get('title', ''),
            'summary': entry.get('summary', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', '')
        }

# --- Функция для более продвинутого анализа текста ---
def analyze_text_for_keywords_advanced(text: str, num_keywords: int = 5) -> List[str]:
    if not text:
        return []
    
    # 1. Очистка и токенизация
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-Я\s]', ' ', text.lower())
    words = cleaned_text.split()
    
    # 2. Инициализация инструментов и объединение стоп-слов
    lemmatizer = WordNetLemmatizer()
    
    # Объединяем стоп-слова для обоих языков, чтобы отфильтровать их все
    try:
        all_stopwords = set(stopwords.words('english')) | set(stopwords.words('russian'))
    except LookupError:
        # Если ресурсы NLTK не были загружены перед тестами (хотя setup_nltk должна была сработать)
        return []

    processed_words = []
    
    for word in words:
        if word not in all_stopwords and len(word) > 2:
            # WordNetLemmatizer работает только с английским. 
            # Для английских слов применяем лемматизацию, для русских оставляем как есть.
            # (Простая эвристика: если слово не содержит кириллицы, пытаемся лемматизировать как английское)
            
            # Проверяем, содержит ли слово кириллицу
            is_russian = any('\u0400' <= char <= '\u04FF' for char in word)
            
            if not is_russian:
                # Предполагаем английское слово и лемматизируем
                lemma = lemmatizer.lemmatize(word)
                processed_words.append(lemma)
            else:
                # Русское слово, оставляем его как есть (для русского нужна другая лемматизация, 
                # но для простоты задачи оставим его нетронутым)
                processed_words.append(word)

    # 3. Подсчет частоты
    word_counts = Counter(processed_words)
    
    # 4. Получение топ N ключевых слов
    most_common = word_counts.most_common(num_keywords)
    
    return [word for word, count in most_common]
