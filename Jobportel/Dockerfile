FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 7860

CMD gunicorn Jobportel.wsgi:application --bind 0.0.0.0:7860 --workers 1 --timeout 300