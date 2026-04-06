# Expedition API

REST API для управління експедиціями. Побудовано на **FastAPI** з архітектурою **DDD / Clean Architecture**.

## Технологічний стек

- **Python 3.13+** / FastAPI / Uvicorn
- **PostgreSQL** + SQLAlchemy 2.x async + asyncpg
- **Alembic** — міграції бази даних
- **dependency-injector** — DI контейнер
- **Docker** / Docker Compose

---

## Вимоги

- Docker та Docker Compose
- Створений Docker network `expedition`:

```bash
docker network create expedition
```

---

## Конфігурація `.env`

Створіть файл `.env` у корені проєкту. Нижче всі доступні змінні:

### База даних

| Змінна               | Обов'язкова | За замовчуванням    | Опис                                     |
|----------------------|:-----------:|---------------------|------------------------------------------|
| `DATABASE_PASSWORD`  | **Так**     | —                   | Пароль до PostgreSQL                     |
| `DATABASE_USER`      | Ні          | `postgres`          | Користувач PostgreSQL                    |
| `DATABASE_NAME`      | Ні          | `expedition`        | Назва бази даних                         |
| `DATABASE_HOST`      | Ні          | `expedition-postgres` | Хост бази даних (ім'я контейнера)      |
| `DATABASE_PORT`      | Ні          | `5432`              | Порт PostgreSQL                          |
| `DATABASE_DIALECT`   | Ні          | `postgresql`        | Діалект (`postgresql`, `sqlite`)         |
| `DATABASE_ECHO`      | Ні          | `false`             | Логування SQL-запитів                    |

### JWT / Безпека

| Змінна                          | Обов'язкова | За замовчуванням         | Опис                                 |
|---------------------------------|:-----------:|--------------------------|--------------------------------------|
| `JWT_TOKEN_SECRET_KEY`          | **Так**     | `dev-only-secret-key-…`  | Секретний ключ для підпису токенів   |
| `JWT_TOKEN_ALGORITHM`           | Ні          | `HS256`                  | Алгоритм JWT                         |
| `JWT_ACCESS_TOKEN_EXPIRE_MINS`  | Ні          | `30`                     | Час життя access-токена (хвилини)    |

### Застосунок

| Змінна        | Обов'язкова | За замовчуванням | Опис                                  |
|---------------|:-----------:|------------------|---------------------------------------|
| `ENVIRONMENT` | Ні          | `prod`           | Середовище: `dev`, `prod`, `test`     |
| `TIMEZONE`    | Ні          | `UTC`            | Часовий пояс                          |

### Uvicorn (опціонально)

| Змінна       | За замовчуванням | Опис              |
|--------------|------------------|-------------------|
| `HOST`       | `0.0.0.0`        | Адреса прослуховування |
| `PORT`       | `8000`           | Порт              |
| `LOG_LEVEL`  | `info`           | Рівень логування  |
| `RELOAD`     | `true`           | Автоперезавантаження |

### Мінімальний `.env` для старту

```env
DATABASE_PASSWORD=your_password
JWT_TOKEN_SECRET_KEY=your-very-secret-key-change-in-production
```

---

## Запуск

### 1. Запустити сховища (PostgreSQL)

```bash
make storages
```

### 2. Запустити застосунок

```bash
make app
```

### 3. Запустити все одразу

```bash
make all
```

API буде доступне за адресою: `http://localhost:8000`

Swagger документація: `http://localhost:8000/docs`

---

## Міграції бази даних

Застосувати всі міграції:

```bash
make migrate
```

Створити нову міграцію:

```bash
make migrations msg="назва міграції"
```

Відкотити до конкретної ревізії:

```bash
make downgrade rev="revision_id"
```

---

## Тести

```bash
# Всі тести (unit + e2e)
make test

# Тільки unit-тести
make test-unit

# Тільки e2e-тести
make test-e2e
```

---

## Корисні команди

```bash
# Логи застосунку
make app-logs

# Shell всередині контейнера
make app-shell

# Зупинити застосунок
make app-down

# Зупинити сховища
make storages-down
```

Повний список команд:

```bash
make help
```

---

## API Routes

Базовий префікс: `/api`

> Позначення доступу: **публічний** — без токена, **auth** — потрібен JWT, **chief** — роль `chief`, **member** — роль `member`

### Auth `/api/auth`

| Метод    | Шлях              | Доступ     | Опис                           |
|----------|-------------------|------------|--------------------------------|
| `POST`   | `/auth/register`  | публічний  | Реєстрація нового користувача  |
| `POST`   | `/auth/login`     | публічний  | Вхід, отримання JWT токена     |

### Users `/api/users`

| Метод  | Шлях               | Доступ | Опис                            |
|--------|--------------------|--------|---------------------------------|
| `GET`  | `/users/me`        | auth   | Профіль поточного користувача   |
| `GET`  | `/users/{user_id}` | auth   | Отримати користувача за ID      |

### Expeditions `/api/expeditions`

| Метод    | Шлях                                   | Доступ | Опис                            |
|----------|----------------------------------------|--------|---------------------------------|
| `GET`    | `/expeditions/`                        | auth   | Список всіх експедицій          |
| `GET`    | `/expeditions/{id}`                    | auth   | Деталі експедиції               |
| `POST`   | `/expeditions/`                        | chief  | Створити експедицію             |
| `PATCH`  | `/expeditions/{id}`                    | chief  | Оновити експедицію              |
| `DELETE` | `/expeditions/{id}`                    | chief  | Видалити експедицію             |
| `PATCH`  | `/expeditions/{id}/status`             | chief  | Змінити статус експедиції       |
| `POST`   | `/expeditions/{id}/members/invite`     | chief  | Запросити учасника              |
| `DELETE` | `/expeditions/{id}/members/{user_id}`  | chief  | Видалити учасника               |
| `POST`   | `/expeditions/{id}/members/confirm`    | member | Підтвердити участь в експедиції |

### WebSocket `/api/ws`

| Протокол | Шлях                         | Доступ          | Опис                                  |
|----------|------------------------------|-----------------|---------------------------------------|
| `WS`     | `/ws/expeditions/{id}`       | auth (учасник)  | Чат експедиції в реальному часі       |

---

## Структура модулів

```
src/
├── modules/
│   ├── auth/          # Автентифікація, JWT, OAuth2
│   ├── users/         # Профілі користувачів
│   ├── expeditions/   # Управління експедиціями
│   └── websocket/     # WebSocket з'єднання
├── adapters/          # Інфраструктура (DB, зовнішні сервіси)
├── common/            # Спільні компоненти, DI контейнери
└── conf/              # Конфігурація застосунку
```
