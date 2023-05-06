# Продуктовый помощник

![example workflow](https://github.com/StAndUP-ru/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта
"Продуктовый помошник" - это сайт для размещения своих рецептов, добавления рецептов в Избранное или в Список покупок из которого можно экспортировать список ингредиентов в формате PDF для совершения закупки. Реализована возможность подписаться на автора рецепта.

## Стек технологий
Python, Django, Django REST Framework, PostgreSQL, Nginx, gunicorn, docker, GitHub Actions, Yandex.Cloud

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
* Перейти в диреуторию проекта:
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
