FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN python manage.py migrate
RUN python manage.py collectstatic
RUN cp -r collected_static/. /front/static/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]
