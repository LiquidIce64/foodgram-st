FROM python:3.11
WORKDIR /app
COPY . .
RUN chmod +x start.sh
RUN pip install -r requirements.txt --no-cache-dir
CMD ["sh", "start.sh"]
