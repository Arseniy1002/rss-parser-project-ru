# parser.py
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
    cleaned_text = re.sub(r'[^a-zA-Zа-яА-Я\s]', '', text.lower())
    words = cleaned_text.split()
    lemmatizer = WordNetLemmatizer()
    english_stopwords = set(stopwords.words('english'))
    russian_stopwords = set(stopwords.words('russian'))
    filtered_words = []
    for word in words:
        if len(word) > 2 and word not in english_stopwords and word not in russian_stopwords:
            filtered_words.append(lemmatizer.lemmatize(word))
    word_counts = Counter(filtered_words)
    return [word for word, count in word_counts.most_common(num_keywords)]