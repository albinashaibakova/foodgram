Проект Foodgram -  это интерактивная платформа, на которой пользователи могут делиться своими рецептами, 
сохранять интересные рецепты в избранное и подписываться на обновления других авторов. 
Основная цель проекта — создать дружелюбное сообщество для любителей готовить и обмениваться кулинарным опытом.
Сайт проекта - [https://foodgramalba.ddns.net/](https://foodgramalba.ddns.net/)


Основные функции
- Публикация рецептов: Пользователи могут добавлять 
свои рецепты с возможностью указания ингредиентов, пошагового приготовления и фотографий.

- Избранное: Возможность добавлять чужие рецепты в личное избранное для быстрого доступа.

- Список покупок: Зарегистрированные пользователи могут создавать списки необходимых продуктов для выбранных блюд.

- Подписки: Пользователи могут подписываться на авторов, чтобы оставаться в курсе новых публикаций.


Технологии

Проект выполнен с использованием современных веб-технологий, таких как HTML, CSS и JavaScript.
Серверная логика реализована с использованием Django REST Framework, а данные хранятся в Postgres.


Установка и запуск

- Клонируйте репозиторий
    `git clone https://github.com/albinashaibakova/foodgram.git`
- Перейдите в директорию backend/
    `cd backend`
- Установите необходимые зависимости из файла requirements.txt
    `pip install -r requirements.txt`
- Примените миграции
    `python manage.py migrate`
- Наполните базу данных необходимыми данными (ингрeдиенты и тэги) с помощью команд
    `python -Xutf8 manage.py migrate_ingredients_from_json data/ingredients.json`
    `python -Xutf8 manage.py migrate_tags_from_json data/tags.json`
- Добавьте файл с секретами, пример файла приведен в .env.example
В режиме отладки в файле с секретами установите значение флага DEGUG=True.
- Установите значение переменной DATABASE_TYPE для подключения к соответствующей БД при запуске проекта.
- Создайте суперпользователя и внесите соответствующие данные и разверните проект
    `python manage.py createsuperuser`
    `python manage.py runserver`
- Для сборки проекта в Docker, воспользуйтесь файлом docker-compose.yml и выполните команду в корне проекта
    `docker compose up`

- Для ознакомления со спецификацией API 
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный 
в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу [http://localhost](http://localhost) изучите фронтенд веб-приложения, а по адресу [http://localhost/api/docs/](http://localhost/api/docs/) — спецификацию API.


Примеры эндпоинтов:

[http://localhost/api/users/](http://localhost/api/users/) - создание и получение информации о пользователях
Методы - GET, POST, HEAD, OPTIONS

[http://localhost/api/users/me/](http://localhost/api/users/me/) - получение личной информации пользователя
Методы - GET, PATCH, HEAD, OPTIONS

[http://localhost/api/users/me/avatar/](http://localhost/api/users/me/avatar/) - установка и удаление аватара пользователя
Методы - PUT, DELETE, OPTIONS

[http://localhost/api/api/users/1/subscribe/](http://localhost/api/api/users/1/subscribe/) - подписка на пользователя
Методы - POST, DELETE, OPTIONS

[http://localhost/api/api/users/subscribtions/](http://localhost/api/api/users/subscribtions/) - получение подписок
Методы - GET, PUT, PATCH, DELETE, HEAD, OPTIONS

[http://localhost/api/recipes/](http://localhost/api/recipes/) - создание и получение информации о рецептах
Методы - GET, POST, HEAD, OPTIONS

[http://localhost/api/recipes/1](http://localhost/api/recipes/1) - получение информации, изменение и удаление рецепта
Методы - GET, PUT, PATCH, DELETE, HEAD, OPTIONS

[http://localhost/api/recipes/1/shopping_cart/](http://localhost/api/recipes/1/shopping_cart/) - добавление и удаление рецепта из корзины
Методы - POST, DELETE, OPTIONS

[http://localhost/api/recipes/1/favorite/](http://localhost/api/recipes/1/favorite/) - добавление и удаление рецепта из избранного
Методы - POST, DELETE, OPTIONS


Автор проекта:
[Альбина Шайбакова](https://github.com/albinashaibakova)


Техно-стек:
python 3.9.8
django 3.2.3
drf 3.12.4
gunicorn 20.1.0
postgres 13.10
nginx 1.22.1
docker 20.10.16
docker-compose 3.8
