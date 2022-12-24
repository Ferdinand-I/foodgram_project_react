# Практикум. Диплом. Сервис Foodgram <img style="margin-left: 10px;" src="https://admprogress.ru/upload/iblock/dcc/Kartinka-obshchepit.jpg" width=64>

Проект **Foodgram** - это сервис для создания и публикации рецептов, который реализован с использованием следующих технологий:
* **Django + Django REST Framework**
* **PosrgreSQL**
* **React**
* **Docker**
* **Nginx**

Основной функционал приложения:
* Регистрация и аутентификация пользователей
* Публикация рецептов с описанием, возможность загружать изображения и присваивать теги
* Возможность подписки на избранных авторов
* Возможность добавлять рецепты в "избранное"
* Возможность добавлять рецепты в список покупок
* Возможность скачать список покупок
* Возможность фильтрации рецептов по тегам
* Предустановленная база разнообразных ингредиентов с возможностью поиска по частичному вхождению
* Возможность изменить пароль

Технические фичи, их реализация:
* Функционал реализован в различных приложениях, так, например, модель пользователей с кастомными полями форм админки можно испортировать в другой Django проект
* Кастомная модель пользователя, что способствует лучшей масштабируемости проекта
* Реализация manage-команды для загрузки data-фикстур
* Проектирование БД через описание моделей с кастомной валидацией полей
* Кастомизация админки
* Создание кастомного поля сериализатора для изображений. Декодирование файла из *base64*
* Реализация функции для скачивания списка покупок. Агрегация данных
* Создание кастомных пермишенов, фильтров, пагинаторов средствами **Django** и сторонних библиотек
* Настройка сервера **Nginx** и запуск приложения в контейнерах **Docker** (backend, frontend, nginx, postgres)


Проект запущен в контейнерах на **ВМ Яндекс.Облака** и доступен по адресу:

http://158.160.6.0/

Данные суперпользователя:

    email: ferdinand@yandex.ru
    password franz12345
    
Данные пользователя без прав администратора:

    email: mary@poppins.ru
    password mary1234

Админка доступна по адресу:

http://158.160.6.0/admin/
