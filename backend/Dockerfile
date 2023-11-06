FROM python:3.9

WORKDIR /app 

RUN pip install gunicorn==20.1.0

# Копируем файл requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# Переходим в директорию foodgram
WORKDIR /app/foodgram

# Запускаем команду manage.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
