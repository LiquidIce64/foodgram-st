# Инструкция по установке
Находясь в папке production, выполните команды:\
```sudo docker compose -f docker-compose.production.yml pull```\
```sudo docker compose -f docker-compose.production.yml up -d```

После этого веб-сайт станет доступен по адресу http://localhost/

Чтобы добавить суперпользователя, выполните команду:\
```sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser```
