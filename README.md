# Проект «Фудграм»

Ссылка на репозиторий: https://github.com/LiquidIce64/foodgram-st

# Инструкция по установке

Находясь в папке production, создайте по примеру .env.example файл .env, заполнив имя пользователя и пароль для базы данных.

Далее, выполните команды:\
```sudo docker compose -f docker-compose.production.yml pull```\
```sudo docker compose -f docker-compose.production.yml up -d```

После этого веб-сайт станет доступен по адресу http://localhost/

Чтобы добавить суперпользователя, выполните команду:\
```sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser```
