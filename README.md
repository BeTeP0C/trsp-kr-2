# TRSP KR-3

Контрольная работа №3 по дисциплине «Технологии разработки серверных приложений».  
Задания 6.1–8.2: HTTP Basic аутентификация, JWT, RBAC, SQLite CRUD.

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

# Скопировать .env.example → .env и при необходимости изменить значения
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

## Тестирование эндпоинтов (curl)

### Задание 6.1–6.2: HTTP Basic Auth

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"user1\",\"password\":\"correctpass\"}" \
  http://localhost:8000/basic/register

# Успешный логин (HTTP Basic)
curl -u user1:correctpass http://localhost:8000/basic/login

# Неверный пароль
curl -u user1:wrongpass http://localhost:8000/basic/login
```

### Задание 6.3: Документация DEV/PROD

```bash
# DEV-режим: доступ к документации с аутентификацией
curl -u admin:admin http://localhost:8000/docs

# Без аутентификации — 401
curl http://localhost:8000/docs

# PROD-режим (MODE=PROD в .env): 404
curl http://localhost:8000/docs
```

### Задание 6.4–6.5: JWT Auth

```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" \
  http://localhost:8000/jwt/register

# Логин — получение токена
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}" \
  http://localhost:8000/jwt/login

# Доступ к защищённому ресурсу (подставить полученный токен)
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/jwt/protected_resource
```

### Задание 7.1: RBAC

```bash
# Регистрация с ролью admin
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"admin1\",\"password\":\"pass\",\"role\":\"admin\"}" \
  http://localhost:8000/rbac/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"admin1\",\"password\":\"pass\",\"role\":\"admin\"}" \
  http://localhost:8000/rbac/login

# Создание ресурса (admin)
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Resource 1\"}" \
  http://localhost:8000/rbac/resource

# Чтение ресурсов (admin, user, guest)
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/rbac/resource

# Обновление (admin, user)
curl -X PUT -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Updated\"}" \
  http://localhost:8000/rbac/resource/1

# Удаление (только admin)
curl -X DELETE -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/rbac/resource/1
```

### Задание 8.1: SQLite — регистрация пользователей

```bash
curl -X POST -H "Content-Type: application/json" \
  -d "{\"username\":\"test_user\",\"password\":\"12345\"}" \
  http://localhost:8000/db/register
```

### Задание 8.2: SQLite — CRUD Todo

```bash
# Создать Todo
curl -X POST -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\"}" \
  http://localhost:8000/todos

# Получить Todo по ID
curl http://localhost:8000/todos/1

# Обновить Todo
curl -X PUT -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread, butter\",\"completed\":true}" \
  http://localhost:8000/todos/1

# Удалить Todo
curl -X DELETE http://localhost:8000/todos/1
```
