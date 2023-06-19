# Продуктовый помощник

![example workflow](https://github.com/StAndUP-ru/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта
"Продуктовый помощник" - это сайт для размещения своих рецептов, добавления рецептов в Избранное или в Список покупок из которого можно экспортировать список ингредиентов в формате PDF для совершения закупки. Реализована возможность подписаться на автора рецепта.

## Стек технологий
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

## Сайт
[http://158.160.27.208/](http://158.160.27.208/)

## Доступ к админке
[http://158.160.27.208/admin/](http://158.160.27.208/admin/)
Логин/пароль: admin

## Документация к API (redoc)
[http://158.160.27.208/api/docs/](http://158.160.27.208/api/docs/)

## Установка проекта локально
* Клонировать репозиторий на локальную машину:
```bash
git clone https://github.com/StAndUP-ru/foodgram-project-react.git
```
* Перейти в директорию проекта:
```bash
cd foodgram-project-react
```
* Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
source venv/Script/activate
```
* Cоздайте файл `.env` в директории `/infra/` с содержанием:
```
DJANGO_KEY=секретный ключ django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
* Установить зависимости из файла requirements.txt:
```bash
pip install -r backend/requirements.txt
```
* Выполните миграции:
```bash
python backend/manage.py migrate
```
* Запустите сервер:
```bash
python backend/manage.py runserver
```


## Запуск проекта в Docker-compose
* Установите Docker-compose и перейдите в директорию `infra/`
* Измените адрес проекта в файле `nginx.conf` на свой
* Запустите docker-compose:
```bash
docker-compose up -d --build
```
* Запустите docker-compose:
```bash
docker-compose up -d --build
```
* Примените миграции:
```bash
docker-compose exec backend python manage.py migrate
```
* Импортируйте в БД ингредиенты:
```bash
docker-compose exec backend python manage.py load_ingredients
```
* Импортируйте в БД теги:
```bash
docker-compose exec backend python manage.py load_tags
```
* Создайте администратора:
```bash
docker-compose exec backend python manage.py createsuperuser
```
* Соберите статику:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```

## Автор backend и deploy:
Андрющенко Станислав

## Разработка frontend:
Яндекс.Практикум
