# test_parser.py
import pytest
from parser import parse_rss_feed_from_text, analyze_text_for_keywords_advanced

# --- Тесты для функции парсинга ---
def test_parse_rss_feed_from_text_valid():
    """Тестируем парсинг валидной RSS-ленты."""
    mock_rss_feed = """
    <rss version="2.0">
        <channel>
            <item>
                <title>Test Title 1</title>
                <link>http://test.com/1</link>
                <description>Test Summary 1</description>
                <pubDate>Mon, 12 Aug 2024 10:00:00 +0300</pubDate>
            </item>
            <item>
                <title>Test Title 2</title>
                <link>http://test.com/2</link>
                <description>Test Summary 2</description>
            </item>
        </channel>
    </rss>
    """
    posts = list(parse_rss_feed_from_text(mock_rss_feed))
    assert len(posts) == 2
    assert posts[0]['title'] == 'Test Title 1'
    assert posts[1]['link'] == 'http://test.com/2'
    assert posts[0]['published'] == 'Mon, 12 Aug 2024 10:00:00 +0300'

def test_parse_rss_feed_from_text_empty():
    """Тестируем парсинг пустой RSS-ленты."""
    mock_rss_feed = "<rss version='2.0'><channel></channel></rss>"
    posts = list(parse_rss_feed_from_text(mock_rss_feed))
    assert len(posts) == 0

# --- Тесты для функции анализа текста ---
def test_analyze_text_for_keywords_basic():
    """Тестируем базовый анализ текста."""
    text = "The Python programming language is powerful and easy to learn. Python is great!"
    keywords = analyze_text_for_keywords_advanced(text, num_keywords=2)
    assert 'python' in keywords
    assert 'programming' in keywords

def test_analyze_text_for_keywords_stopwords():
    """Тестируем удаление стоп-слов."""
    text = "Эта статья о том, как использовать Python и Django для создания веб-приложений."
    keywords = analyze_text_for_keywords_advanced(text, num_keywords=3)
    assert 'python' in keywords
    assert 'django' in keywords
    assert 'создания' in keywords
    assert 'как' not in keywords
    assert 'использовать' not in keywords

def test_analyze_text_for_keywords_empty():
    """Тестируем пустой текст."""
    keywords = analyze_text_for_keywords_advanced("")
    assert keywords == []