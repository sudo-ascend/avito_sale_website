# Grachev Studio

Публичный Django-проект веб-студии с:

- главной страницей
- портфолио проектов
- формой ТЗ с отправкой письма на почту
- Django admin для управления контентом

## Стек

- Python 3.13
- Django 5
- SQLite3
- Bootstrap 5
- Pillow
- WeasyPrint

## Структура

- `config` - настройки проекта и роутинг
- `core` - главная страница, контакты и общие модели
- `portfolio` - проекты портфолио, технологии, изображения
- `briefs` - форма ТЗ, вложения и email-уведомления
- `templates` - шаблоны
- `static` - CSS и JavaScript

## Запуск

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Полезные команды

```powershell
python manage.py check
python manage.py test
```

## Что редактируется через админку

- контакты и контент главной страницы
- секция кейса на главной
- услуги
- проекты портфолио
- изображения проектов и их `alt`
- порядок показа проектов в каталоге
- список технологий
- заявки из формы ТЗ
