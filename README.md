# Task Manager

Простий менеджер проєктів і задач на Django з HTMX/Alpine.js/Bootstrap.

## Вимоги

- Python 3.13
- PostgreSQL 15+ локально **або** Docker (рекомендовано)

## Можливості

- CRUD для проєктів
- CRUD для задач із пріоритетами та дедлайнами
- HTMX‑взаємодії без перезавантаження сторінки
- Ізоляція даних користувачів через django‑allauth

## Як запустити локально (Docker)

```bash
docker compose up --build
```

Доступ: `http://localhost:8000`

Примітка: `0.0.0.0` — це адреса привʼязки сервера, а не URL для браузера.

## Як запустити локально (без Docker)

### 1) Віртуальне середовище

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2) Встановлення залежностей

```bash
pip install -r requirements.txt
```

### 3) Змінні середовища (PowerShell)

```powershell
$env:DJANGO_SECRET_KEY = "change-me"
$env:DJANGO_DEBUG = "1"
$env:DJANGO_ALLOWED_HOSTS = "*"
$env:DB_NAME = "task"
$env:DB_USER = "task"
$env:DB_PASSWORD = "task"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
```

### 4) Міграції та запуск

```bash
python manage.py migrate
python manage.py runserver
```

Відкрий: `http://localhost:8000` або `http://127.0.0.1:8000`

## Змінні середовища

| Змінна | За замовчуванням | Опис |
| --- | --- | --- |
| DJANGO_SECRET_KEY | change-me | Секретний ключ Django |
| DJANGO_DEBUG | 1 | Режим дебагу (1 або 0) |
| DJANGO_ALLOWED_HOSTS | * | Дозволені хости через кому |
| DB_NAME | task | Назва БД |
| DB_USER | task | Користувач БД |
| DB_PASSWORD | task | Пароль БД |
| DB_HOST | localhost | Хост БД |
| DB_PORT | 5432 | Порт БД |

## Архітектура та бізнес‑логіка

- `app/` — налаштування Django, URL‑и, конфіг.
- `main/` — головна сторінка (dashboard).
- `service/` — бізнес‑логіка домену:
  - `service/models.py` — моделі Project/Task.
  - `service/forms.py` — серверна валідація та правила.
  - `service/views.py` — сценарії створення/оновлення/видалення, зміна пріоритетів.
  - `service/urls.py` — HTMX‑ендпоінти для partial‑оновлень.
- `users/` — кастомна модель користувача, допоміжна логіка auth.
- `templates/` — HTML‑шаблони й partial‑фрагменти.
- `static/` — CSS/JS для UI‑поведінки.

**Де бізнес‑логіка:** у `service/views.py` (потоки CRUD і пріоритети) та `service/forms.py` (валідація).

## Документація в коді

- Коментарі додаються тільки для неочевидної логіки (HTMX‑потоки, пріоритети).
- Більшість HTML‑дій документовано коментарями в `templates/`.
- Логіка клієнтської валідації описана в `static/js/app.js`.

## Іменування змінних/класів

- Доменно‑орієнтовані назви: `Project`, `Task`, `deadline`, `priority`.
- Імена функцій описують дію: `task_create`, `task_update`, `task_move`.
- Локальні змінні короткі, але зрозумілі (`project`, `task`, `form`).

## Оптимізація

- Операції з задачами обмежені користувачем (`project__owner=request.user`).
- Перестановка задач виконується в транзакції з `select_for_update`.
- Сортування задач через `priority` забезпечує стабільний порядок.

## Тести

Запуск:

```bash
python manage.py test
```

Покриті сценарії:

- доступ до dashboard
- CRUD проєктів і задач
- дедлайни та валідація
- перестановка задач (priority)
- ізоляція даних по користувачах
- empty‑state рендеринг

## Лінтинг

Ruff налаштований через pre‑commit:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Альтернатива:

```bash
ruff check .
```

## Git‑коміти (семантичні)

Рекомендований формат:

- `feat: додати підсвітку дедлайнів`
- `fix: виправити валідацію дати`
- `docs: оновити README`
- `test: додати тести CRUD`

## Нотатки

- Відповіді по SQL — у `SQL.md`
- Docker використовує PostgreSQL 16 за замовчуванням
