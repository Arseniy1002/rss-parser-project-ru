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
        # Проверяем наличие ресурсов
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
    
    # 1. Токенизация и очистка: 
    # Используем re.findall для извлечения только слов (последовательностей букв) 
    # длиной 3 и более, что автоматически фильтрует мусор, знаки препинания и короткие стоп-слова.
    words = re.findall(r'[a-zA-Zа-яА-Я]{3,}', text.lower())
    
    # 2. Инициализация инструментов и объединение стоп-слов
    lemmatizer = WordNetLemmatizer()
    
    try:
        # Объединяем стоп-слова для обоих языков (английский и русский)
        all_stopwords = set(stopwords.words('english')) | set(stopwords.words('russian'))
    except LookupError:
        logging.error("NLTK stopwords не загружены.")
        return []

    processed_words = []
    
    for word in words:
        # Проверка на стоп-слова
        if word in all_stopwords:
            continue
            
        # Определяем, является ли слово русским (содержит ли кириллицу)
        is_russian = any('\u0400' <= char <= '\u04FF' for char in word)
            
        if not is_russian:
            # Английское слово: применяем лемматизацию
            lemma = lemmatizer.lemmatize(word)
            processed_words.append(lemma)
        else:
            # Русское слово: добавляем как есть (WordNetLemmatizer не поддерживает русский)
            processed_words.append(word)

    # 3. Подсчет частоты
    word_counts = Counter(processed_words)
    
    # 4. Получение топ N ключевых слов
    most_common = word_counts.most_common(num_keywords)
    
    return [word for word, count in most_common]
