# Backend

API системы оценивания проектов: FastAPI, PostgreSQL, слои репозиториев и сервисов (DDD-подход).

[Wiki](wiki/index.md)

---

## Для коллег: быстрый старт

### Что нужно

- **Python 3.11+**
- **PostgreSQL** (локально или через Postgres.app и т.п.)
- Файл **`.env`** в корне проекта (см. ниже)

### 1. Окружение и зависимости

```bash
# Клонировать репозиторий и перейти в папку backend
cd backend

# Вариант с uv (рекомендуется)
uv sync

# Или через pip
pip install -e ".[dev]"
# Дополнительно: asyncpg, pydantic[email], pwdlib[argon2], python-multipart, email-validator
```

### 2. База данных и .env

Создайте файл **`.env`** в корне проекта (рядом с `pyproject.toml`):

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/DATABASE_NAME
SECRET_KEY=your-secret-key-for-jwt
```

Пример без пароля (локальный пользователь БД = имя базы):

```env
DATABASE_URL=postgresql+asyncpg://amish88r@localhost:5432/amish88r
```

При первом запуске приложения таблицы создаются автоматически (`Base.metadata.create_all` в `main.py`).

### 3. Запуск сервера

```bash
# Из корня backend
uvicorn src.main:app --reload
```

Сервер будет доступен по адресу **http://localhost:8000**.

- **Swagger UI**: http://localhost:8000/docs  
- **Корень API**: http://localhost:8000/  
- **Версия API**: префикс `/v1` (например, `/v1/auth/token`, `/v1/evaluations/`)

### 4. Тестовые данные (для проверки API)

Чтобы не вводить данные вручную, можно заполнить БД тестовыми пользователями и проектом:

```bash
python scripts/seed_test_data.py
```

Скрипт создаёт:

- пользователя **teacher@test.com** (преподаватель/оценщик);
- пользователя **student@test.com** (студент);
- один проект с владельцем-студентом и его участие в проекте.

В консоль выводятся **ID проекта, ID студента, ID преподавателя**. Пароль для обоих: **test1234**. Эти данные можно использовать в Swagger для теста `POST /v1/evaluations/` и `GET /v1/evaluations/results/by-project/{project_id}`.

---

## Структура API (v1)

| Раздел        | Префикс       | Описание |
|---------------|---------------|----------|
| Аутентификация | `/v1/auth`    | Токен (логин), выход |
| Пользователи  | `/v1/users`   | CRUD пользователей |
| Проекты       | `/v1/projects`| CRUD проектов, список с пагинацией |
| Резюме        | `/v1/resumes` | CRUD резюме |
| Сессии        | `/v1/sessions`| Управление сессиями пользователя |
| Аудит         | `/v1/audit`   | Логи изменений (по user_id) |
| Оценивание    | `/v1/evaluations` | Форма оценивания и форма представления результатов |

Основные эндпоинты оценивания:

- **POST** `/v1/evaluations/` — отправить оценку (тело: `project_id`, `participant_id`, `scores`, опционально `comment`).
- **GET** `/v1/evaluations/results/by-project/{project_id}` — сводные результаты по проекту.

Авторизация: в Swagger нажать «Authorize» и ввести токен, полученный через **POST /v1/auth/token** (username = email, password = пароль пользователя).

---

## Структура проекта

```
backend/
├── src/
│   ├── api/v1/          # Роуты и эндпоинты
│   ├── core/             # Конфиг, БД, безопасность, зависимости, аудит
│   ├── model/            # SQLAlchemy-модели (models.py)
│   ├── repository/       # Слой доступа к данным
│   ├── schema/           # Pydantic-схемы для запросов/ответов
│   └── services/         # Бизнес-логика
├── scripts/
│   └── seed_test_data.py # Скрипт тестовых данных
├── .env                  # Не коммитить: DATABASE_URL, SECRET_KEY и др.
├── pyproject.toml
└── README.md
```

Зависимости и запуск через **uv** см. в начале файла; при использовании **pip** все пакеты из `pyproject.toml` должны быть установлены в окружение.

---

## Разработка и качество кода

### Ruff (линтер и форматирование)

```bash
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .
```

Конфигурация — в `pyproject.toml` ([tool.ruff]).

### Pre-commit

```bash
pre-commit install
pre-commit run --all-files
```

### Запуск без uv

Если не используете uv:

```bash
pip install -e ".[dev]"
uvicorn src.main:app --reload
```

При необходимости скорректируйте `DATABASE_URL` в `.env` под свою локальную БД.
