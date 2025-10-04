# Dockerfile
# Используем официальный образ Python как базовый
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# Копируем и устанавливаем зависимости
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root

# Скачиваем необходимые ресурсы NLTK
RUN poetry run python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords'); nltk.download('omw-1.4')"

# Копируем все файлы проекта в контейнер
COPY . .

# Команда для запуска приложения
CMD ["poetry", "run", "python", "main.py"]