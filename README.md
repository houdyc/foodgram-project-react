# Foodgram-project
![example workflow](https://github.com/loren166/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Foodgram-project - это проект в котором авторизованные пользователи могут создавать свои рецепты, так же все созданные рецепты появляются на главной странице от всех пользователей, и можно добавить любой понравившийся рецепт к себе в избранное чтобы не потерять его,
а если понравились несколько рецептов от одного автора - можно подписаться на него и не пропускать ни одного его рецепта, и конечно же для вашего удобства - в списке покупок можно скачать себе список ингредиентов рецепта или несколько рецептов в txt файле.

На сайте пристутствует фильтрация по тегам, создавать которые может только администратор.

Все выше перечисленное доступно только для авторизованных пользователей, те кто не хочет регистрироваться на сайте - могут только посмотреть уже созданные рецепты на главной.

Для автоматизации развертывания на боевых серверах используется среда виртуализации Docker, а также Docker-compose - инструмент для запуска многоконтейнерных приложений.

## Стек технологий:
>Python | 
>Django | 
>Django Rest Framework | 
>Rest API | 
>Djoser | 
>PostgreSQL | 
>Docker |
>Gunicorn |
>Nginx |
> GitHub Actions |
> Yandex.cloud |

## .env
```
В директории /infra вы можете создать файл .env который вам нужно заполнить по следующему образцу:
DB_ENGINE=
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
```
## Запуск проекта в контейнерах
```
docker-compose up
```

## Команды для выполнения миграций в контейнерах и загрузки ингредиентов в бд.

### Миграции

```
docker-compose exec backend python manage.py makemigrations users
docker-compose exec backend python manage.py migrate users
docker-compose exec backend python manage.py makemigrations api
docker-compose exec backend python manage.py migrate api
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполнение бд

```
docker-compose exec backend python manage.py load_ingredients
```

## Документация
Документация будет доступна по эндпоинту /redoc/.