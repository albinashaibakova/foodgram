Проект Foodgram -  это интерактивная платформа, на которой пользователи могут делиться своими рецептами, 
сохранять интересные рецепты в избранное и подписываться на обновления других авторов. 
Основная цель проекта — создать дружелюбное сообщество для любителей готовить и обмениваться кулинарным опытом.
Сайт проекта - https://foodgramalba.ddns.net/


Основные функции
- Публикация рецептов: Пользователи могут добавлять 
свои рецепты с возможностью указания ингредиентов, пошагового приготовления и фотографий.

- Избранное: Возможность добавлять чужие рецепты в личное избранное для быстрого доступа.

- Список покупок: Зарегистрированные пользователи могут создавать списки необходимых продуктов для выбранных блюд.

- Подписки: Пользователи могут подписываться на авторов, чтобы оставаться в курсе новых публикаций.


Страницы веб-приложения

- Главная: Отображает первые шесть рецептов, отсортированных по дате публикации (от новых к старым) с постраничной 
пагинацией для оставшихся рецептов.

- Страница входа: Формы для ввода имейла и пароля для доступа к личному кабинету.

- Страница регистрации: Возможность создать новый аккаунт через форму регистрации.

- Страница рецепта: Подробная информация о каждом рецепте, включая ингредиенты и пошаговые инструкции.

- Страница пользователя: Профиль пользователя с информацией о его рецептах и подписках.

- Страница подписок: Позволяет пользователю управлять списком подписок на авторов.

- Избранное: Обзор сохраненных рецептов пользователя.

- Список покупок: Инструмент для создания и управления списками продуктов.

- Создание и редактирование рецепта: Формы для добавления нового рецепта или редактирования существующего.

- Страница смены пароля: Форма для редактирования пароля.

- Статические страницы: "О проекте" и "Технологии" — информация о проекте и используемых технологиях.


Технологии

Проект выполнен с использованием современных веб-технологий, таких как HTML, CSS и JavaScript.
Серверная логика реализована с использованием Django REST Framework, а данные хранятся в Postgres.


Установка и запуск

- Клонируйте репозиторий
    `git clone`
- Установите необходимые зависимости из файла requirements.txt
    `pip install -r requirements.txt`
- Создайте и примените миграции
    `python manage.py makemigrations`
    `python manage.py migrate`
- Наполните базу данных необходимыми данными (ингридиенты и тэги) с помощью команды
    `python -Xutf8 manage.py migrate_from_json путь_к_папке/ingredients.json`
В режиме отладки в файле settings.py требуется раскоментировать строки 103-108, 
отвечающие за подключение к базе данных Sqlite и закоментировать строки, связанные с плдключением к БД Postgres
Также указать значение флага DEBUG = True
- Создайте суперпользователя и внесите соответствующие данные и разверните проект
    `python manage.py createsuperuser`
    `python manage.py runserver`
- Добавьте файл с секретами, пример файла приведен в .env.example
- Для сборки проекта в Docker, воспользуйтесь файлом docker-compose.yml
    `docker compose up`

- Для ознакомления со спецификацией API 
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный 
в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.


Примеры эндпоинтов:

http://localhost/api/users/ - создание и получение информации о пользователях
Методы - GET, POST, HEAD, OPTIONS

http://localhost/api/users/me/ - получение личной информации пользователя
Методы - GET, PATCH, HEAD, OPTIONS

http://localhost/api/users/me/avatar/ - установка и удаление аватара пользователя
Методы - PUT, DELETE, OPTIONS

http://localhost/api/api/users/1/subscribe/ - подписка на пользователя
Методы - POST, DELETE, OPTIONS

http://localhost/api/api/users/subscribtions/ - получение подписок
Методы - GET, PUT, PATCH, DELETE, HEAD, OPTIONS

http://localhost/api/recipes/ - создание и получение информации о рецептах
Методы - GET, POST, HEAD, OPTIONS

http://localhost/api/recipes/1 - получение информации, изменение и удаление рецепта
Методы - GET, PUT, PATCH, DELETE, HEAD, OPTIONS

http://localhost/api/recipes/1/shopping_cart/ - добавление и удаление рецепта из корзины
Методы - POST, DELETE, OPTIONS

http://localhost/api/recipes/1/favorite/ - добавление и удаление рецепта из избранного
Методы - POST, DELETE, OPTIONS


Автор проекта:
Альбина Шайбакова