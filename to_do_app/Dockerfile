FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория внутри контейнера
WORKDIR /code

# Копируем файлы проекта
COPY . /code/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt