# Grachev Studio CRM

Полноценный Django-проект для веб-студии с публичным сайтом, формой ТЗ, внутренней CRM, бухгалтерией, Excel-выгрузкой, DNS-мониторингом и email-напоминаниями по срокам.

## Стек

- Python 3.13
- Django 5
- Django REST Framework
- SQLite3
- Bootstrap 5
- openpyxl
- cryptography
- dnspython

## Структура

- `config` — настройки проекта, роутинг
- `core` — главная, контакты, дашборд, экспорт, базовые утилиты
- `portfolio` — проекты портфолио и технологии
- `briefs` — форма ТЗ и хранение заявок
- `crm` — клиенты и заказы
- `accounting` — доходы и расходы
- `dns_monitor` — цели DNS-мониторинга и логи проверок
- `notifications` — правила напоминаний и логи уведомлений
- `templates` — общие шаблоны
- `static` — CSS и JS

## Установка

1. Создай и активируй виртуальное окружение:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Установи зависимости:

```powershell
pip install -r requirements.txt
```

3. Проверь `.env`.

Для локального запуска уже создан `.env` с консольным email backend. Чтобы письма уходили реально, замени `EMAIL_BACKEND` на SMTP и заполни `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`.

4. Выполни миграции:

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. Загрузи тестовые данные:

```powershell
python manage.py seed_demo_data --create-manager
```

Тестовый менеджер:

- логин: `manager`
- пароль: `Manager12345!`

6. При необходимости создай суперпользователя:

```powershell
python manage.py createsuperuser
```

7. Запусти сервер:

```powershell
python manage.py runserver
```

## Полезные команды

Проверка проекта:

```powershell
python manage.py check
```

Проверка DNS вручную:

```powershell
python manage.py check_dns_updates
```

Отправка напоминаний вручную:

```powershell
python manage.py send_expiry_notifications
```

Вызов внутренних API-эндпоинтов фоновых задач:

```powershell
python manage.py run_internal_jobs
```

## Внутренние API для фоновых задач

- `POST /dashboard/dns/api/internal/dns-check/`
- `POST /dashboard/notifications/api/internal/notifications/run/`

Для доступа нужен заголовок:

```text
X-Internal-Api-Key: <INTERNAL_API_TOKEN>
```

## Автоматизация в продакшене

Для продакшена рекомендуется запускать фоновые задачи через `cron`, Windows Task Scheduler или systemd timer:

- раз в 10-30 минут вызывать DNS endpoint
- раз в сутки вызывать endpoint напоминаний

Пример для PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/dashboard/dns/api/internal/dns-check/" -Headers @{ "X-Internal-Api-Key" = "change-me" }
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/dashboard/notifications/api/internal/notifications/run/" -Headers @{ "X-Internal-Api-Key" = "change-me" }
```

## Безопасность

- Пароли к серверам не хранятся в открытом виде: используется шифрование через `cryptography`.
- Для продакшена обязательно задай отдельный `FIELD_ENCRYPTION_KEY` в `.env`.
- Внутренние API защищены `INTERNAL_API_TOKEN`.
- Публичной регистрации нет, вход доступен только `is_staff` пользователям.

## Выгрузка Excel

Из дашборда доступны `.xlsx`-выгрузки:

- клиенты
- заказы
- бухгалтерия
- подписки / домены / оплаты
