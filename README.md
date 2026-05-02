# TRSP KR-3 / KR-4

Контрольные работы №3-4 по дисциплине «Технологии разработки серверных приложений».

- **KR-3** (задания 6.1-8.2): HTTP Basic аутентификация, JWT, RBAC, SQLite CRUD
- **KR-4** (задания 9.1-11.2): Alembic-миграции, обработка ошибок, валидация, тестирование

## Установка и запуск

```bash
# Клонировать репозиторий
git clone <url> && cd trsp-kr-2

# Создать виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Скопировать .env.example -> .env
copy .env.example .env

# Запустить приложение
uvicorn main:app --reload
```

Приложение будет доступно по адресу http://localhost:8000

## Переменные окружения

| Переменная             | Описание                                      | По умолчанию           |
|------------------------|-----------------------------------------------|------------------------|
| `SECRET_KEY`           | Секретный ключ для подписи токенов             | `change-me`            |
| `SESSION_DURATION`     | Время жизни cookie-сессии (сек)                | `300`                  |
| `RENEWAL_THRESHOLD`    | Порог обновления сессии (сек)                  | `180`                  |
| `MODE`                 | Режим работы: `DEV` или `PROD`                 | `DEV`                  |
| `DOCS_USER`            | Логин для доступа к /docs (DEV)                | `admin`                |
| `DOCS_PASSWORD`        | Пароль для доступа к /docs (DEV)               | `admin`                |
| `JWT_EXPIRATION_MINUTES` | Время жизни JWT-токена (мин)                 | `30`                   |

## Alembic-миграции (задание 9.1)

```bash
# Инициализация уже выполнена. Для применения миграций:
alembic upgrade head

# Для создания новой миграции после изменения моделей:
alembic revision --autogenerate -m "описание изменений"
```

Миграции находятся в `alembic/versions/`. Создано две миграции:
1. Создание таблицы `products` (id, title, price, count)
2. Добавление поля `description` (NOT NULL)

## Запуск тестов (задания 11.1-11.2)

```bash
# Запуск всех тестов
python -m pytest tests/ -v

# Только синхронные тесты (11.1)
python -m pytest tests/test_endpoints.py -v

# Только асинхронные тесты (11.2)
python -m pytest tests/test_async_users.py -v
```

## Тестирование эндпоинтов (curl)

### Задание 6.1-6.2: HTTP Basic Auth

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}' \
  http://localhost:8000/basic/register

# Логин (HTTP Basic)
curl -u user1:correctpass http://localhost:8000/basic/login

# Неверный пароль
curl -u user1:wrongpass http://localhost:8000/basic/login
```

### Задание 6.3: Документация DEV/PROD

```bash
# DEV: доступ к документации с аутентификацией
curl -u admin:admin http://localhost:8000/docs

# PROD (MODE=PROD в .env): 404
curl http://localhost:8000/docs
```

### Задание 6.4-6.5: JWT Auth

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/jwt/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/jwt/login

# Защищённый ресурс
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/jwt/protected_resource
```

### Задание 7.1: RBAC

```bash
# Регистрация с ролью admin
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pass","role":"admin"}' \
  http://localhost:8000/rbac/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pass","role":"admin"}' \
  http://localhost:8000/rbac/login

# CRUD-операции с ресурсами (подставить токен)
curl -X POST -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"name":"Resource 1"}' http://localhost:8000/rbac/resource
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/rbac/resource
```

### Задание 8.1-8.2: SQLite

```bash
# Регистрация в SQLite
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}' \
  http://localhost:8000/db/register

# Todo CRUD
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs"}' \
  http://localhost:8000/todos
curl http://localhost:8000/todos/1
curl -X PUT -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread","completed":true}' \
  http://localhost:8000/todos/1
curl -X DELETE http://localhost:8000/todos/1
```

### Задание 10.1: Пользовательские ошибки

```bash
# Получить существующий товар
curl http://localhost:8000/errors/items/1

# Товар не найден (CustomExceptionB -> 404)
curl http://localhost:8000/errors/items/999

# Покупка с недостаточным запасом (CustomExceptionA -> 400)
curl -X POST "http://localhost:8000/errors/items/2/purchase?quantity=1"
```

### Задание 10.2: Валидация данных

```bash
# Валидные данные
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","age":25,"email":"test@mail.com","password":"securepass1"}' \
  http://localhost:8000/validate/user

# Невалидный возраст (<=18)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","age":17,"email":"test@mail.com","password":"securepass1"}' \
  http://localhost:8000/validate/user
```

### Задание 11.1-11.2: Users CRUD (для тестов)

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","age":25}' http://localhost:8000/users
curl http://localhost:8000/users/1
curl -X DELETE http://localhost:8000/users/1
```
