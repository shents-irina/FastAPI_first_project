# API для сервиса бронирования отелей

Учебный backend-сервис для поиска отелей и номеров, регистрации пользователей и бронирования номеров на выбранные даты.
Приложение построено на FastAPI, использует асинхронный доступ к PostgreSQL, JWT-аутентификацию в cookie, кэширование и фоновые задачи Celery.

## Возможности

- регистрация, вход и выход пользователя;
- JWT-аутентификация через cookie;
- создание, просмотр, изменение и удаление отелей и номеров;
- создание, просмотр и удаление удобств номера;
- пагинация списка отелей и фильтрация по названию и местоположению;
- поиск отелей и свободных номеров на выбранные даты;
- создание бронирований с проверкой дат и доступности номера;
- просмотр бронирований текущего пользователя;
- отмена бронирования текущего пользователя с проверкой дат;
- кэширование отдельных запросов в Redis с резервным in-memory-кэшем;
- загрузка изображений и создание уменьшенных копий в фоновой задаче;
- ежедневная рассылка email-напоминаний о заезде через Celery;
- миграции базы данных Alembic;
- unit- и integration-тесты на pytest.

## Технологии

- **Python 3.13** - язык проекта;
- **FastAPI** и **Uvicorn** - веб-фреймворк, сервер для его запуска;
- **Pydantic** и **pydantic-settings** - схемы запросов и ответов, загрузка настроек из `.env`;
- **PostgreSQL 17**, **SQLAlchemy 2** и **asyncpg** - хранение данных и асинхронный доступ к ним;
- **Alembic** - миграции схемы базы данных;
- **PyJWT**, **passlib** и **bcrypt** - JWT-токены и хеширование паролей;
- **Redis** и **fastapi-cache2** - кэширование запросов; если Redis недоступен, используется in-memory-кэш;
- **Celery** (worker и Beat) - фоновые и периодические задачи;
- **Pillow** - создание уменьшенных копий загруженных изображений;
- **smtplib** (стандартная библиотека) - отправка писем через SMTP;
- **pytest**, **pytest-asyncio** и **HTTPX** - unit- и integration-тесты;
- **Docker** и **Docker Compose** - запуск API, Celery worker и Celery Beat в контейнерах.

## Структура проекта

```
.
├── src
│   ├── api                   # эндпоинты FastAPI (роутеры) и зависимости
│   ├── connectors            # клиенты внешних сервисов (Redis)
│   ├── migrations            # миграции Alembic
│   ├── models                # ORM-модели SQLAlchemy (таблицы БД)
│   ├── repositories          # работа с БД: запросы и маппинг моделей в схемы
│   ├── schemas               # Pydantic-схемы запросов и ответов
│   ├── services              # бизнес-логика (авторизация, бронирование и др.)
│   ├── static                # статические файлы; в images/ сохраняются загруженные изображения
│   ├── tasks                 # фоновые и периодические задачи Celery
│   ├── utils                 # вспомогательные модули (DBManager, EmailManager)
│   ├── config.py             # настройки приложения из переменных окружения (.env)
│   ├── database.py           # подключение к PostgreSQL, сессии и базовый класс моделей
│   ├── exceptions.py         # собственные исключения приложения
│   ├── init.py               # общие объекты приложения (менеджер Redis)
│   └── main.py               # точка входа: создание приложения FastAPI и подключение роутеров
├── tests
│   ├── integration_tests     # тесты API и работы с БД
│   ├── unit_tests            # тесты отдельной логики
│   ├── conftest.py           # общие фикстуры pytest
│   ├── mock_hotels.json      # тестовые данные отелей
│   └── mock_rooms.json       # тестовые данные номеров
├── .env-example              # шаблон файла с настройками
├── .dockerignore             # файлы, которые не попадают в Docker-образ
├── .gitignore                # файлы, которые не попадают в Git
├── .python-version           # версия Python для проекта
├── Dockerfile                # образ приложения
├── Makefile                  # короткие команды для запуска и миграций
├── README.md                 # описание проекта
├── alembic.ini               # настройки Alembic
├── docker-compose.yml        # запуск API, Celery worker и Celery Beat в контейнерах
├── pyproject.toml            # настройки проекта, ruff, pyright и pytest
└── requirements.txt          # зависимости Python
```

## Подготовка и запуск приложения

Приложение можно запустить локально двумя способами:

| | Через Docker | Без Docker |
| --- | --- | --- |
| API, PostgreSQL и Redis | В контейнерах | Напрямую на вашем компьютере |
| Порты PostgreSQL и Redis на компьютере | `6432` и `7379` | `5432` и `6379` |
| Адрес API | <http://127.0.0.1:8008/docs> | <http://127.0.0.1:8000/docs> |

Порты PostgreSQL и Redis в двух способах разные, поэтому они не конфликтуют, даже если запущены одновременно.

### Клонируйте репозиторий и перейдите в его папку

```console
git clone https://github.com/shents-irina/FastAPI_first_project.git
cd FastAPI_first_project
```

### Создайте файл с настройками

macOS и Linux:
```bash
cp .env-example .env
```

Windows:
```powershell
copy .env-example .env
```

### Заполните `.env`

Файл `.env` содержит секреты (пароли, ключ JWT), поэтому он добавлен в `.gitignore`.
**Не публикуйте и не коммитьте его**: в репозитории должен остаться только шаблон `.env-example`.

Описание переменных окружения:
| Переменная | Назначение |
| --- | --- |
| `MODE` | Режим приложения: `LOCAL`, `DEV`, `PROD` или `TEST` |
| `DB_HOST`, `DB_PORT` | Подключение БД (адрес и порт PostgreSQL) |
| `DB_USER`, `DB_PASS`, `DB_NAME` | Данные для подключения к базе |
| `REDIS_HOST`, `REDIS_PORT` | Подключение к Redis (адрес и порт Redis) |
| `JWT_SECRET_KEY` | Секрет для подписи JWT |
| `JWT_ALGORITHM` | Алгоритм подписи JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Срок действия токена в минутах |
| `SMTP_HOST`, `SMTP_PORT` | Адрес и порт почтового сервера |
| `SMTP_USER`, `SMTP_PASS` | Данные почтового аккаунта |

В `.env-example` уже указаны значения для локального запуска (`MODE=LOCAL`, `DB_HOST=localhost`, `REDIS_HOST=localhost` и стандартные порты `5432` и `6379`).

`DB_USER`, `DB_PASS`, `DB_NAME` должны совпадать с данными PostgreSQL (подробнее ниже).

`JWT_SECRET_KEY` - замените `change-me` на случайную строку. Сгенерировать её можно командой:

  macOS и Linux:
  ```bash
  openssl rand -hex 32
  ```
  или
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  Windows:
  ```powershell
  py -3.13 -c "import secrets; print(secrets.token_hex(32))"
  ```
`SMTP_*` — настройки почты нужны только для отправки напоминаний о заезде (Celery).

Для остальных функций можно оставить значения из примера, но все переменные должны быть заполнены.

### Запуск приложения через Docker Compose (рекомендуется)

Если Docker не установлен, установите [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Файл `docker-compose.yml` запускает API, Celery worker и Celery Beat в контейнерах.
PostgreSQL и Redis в него не входят: они запускаются отдельно и должны находиться в той же
Docker-сети `my-network`, которая указана в `docker-compose.yml` как внешняя.

#### 1. Подготовьте сеть, PostgreSQL и Redis
Создайте сеть:

```console
docker network create my-network
```

Если контейнеры `booking-db` и `booking-cache` уже созданы, подключите их к сети:
```console
docker network connect my-network booking-db
docker network connect my-network booking-cache
```

Если контейнеров ещё нет, создайте их командами ниже: в них уже указана нужная сеть (`--network my-network`).

Значения `POSTGRES_USER`, `POSTGRES_PASSWORD` и `POSTGRES_DB` должны совпадать с `DB_USER`,
`DB_PASS` и `DB_NAME` из `.env`.

Запустите PostgreSQL и Redis в контейнерах:

macOS и Linux:
```bash
docker run -d \
  --name booking-db \
  --network my-network \
  -p 6432:5432 \
  -e POSTGRES_USER=booking_user \
  -e POSTGRES_PASSWORD=change-me \
  -e POSTGRES_DB=booking \
  --volume pg-booking-data:/var/lib/postgresql/data \
  postgres:17

docker run -d \
  --name booking-cache \
  --network my-network \
  -p 7379:6379 \
  redis:8
```

Windows:
```powershell
docker run -d `
  --name booking-db `
  --network my-network `
  -p 6432:5432 `
  -e POSTGRES_USER=booking_user `
  -e POSTGRES_PASSWORD=change-me `
  -e POSTGRES_DB=booking `
  --volume pg-booking-data:/var/lib/postgresql/data `
  postgres:17

docker run -d `
  --name booking-cache `
  --network my-network `
  -p 7379:6379 `
  redis:8
```

> Про порты: слева от двоеточия в `-p` стоит порт на вашем компьютере, справа порт внутри контейнера. Здесь используются `6432` и `7379`, чтобы не конфликтовать с PostgreSQL и Redis, установленными локально.
>
> Контейнеры API, worker и Beat обращаются к базе и Redis внутри сети Docker, поэтому в `.env` для них указываются порты контейнеров (`5432` и `6379`), а не порты `6432` и `7379` на вашем компьютере. Порты `6432` и `7379` нужны только для подключения с вашей машины (например, из DBeaver, `psql` или при запуске тестов).

Команды `docker run` нужно выполнить один раз.
В следующий раз запускайте уже созданные контейнеры:
```console
docker start booking-db booking-cache
```

Команда, если нужно будет остановить контейнеры:
```console
docker stop booking-cache booking-db
```

#### 2. Измените адреса сервисов в `.env`

Внутри Docker-сети сервисы доступны по именам контейнеров.
Не забудьте, что `DB_USER`, `DB_PASS` и `DB_NAME` должны совпадать со значениями `POSTGRES_*` из команды `docker run`.

```dotenv
DB_HOST=booking-db
DB_PORT=5432
REDIS_HOST=booking-cache
REDIS_PORT=6379
```

#### 3. Запустите приложение

```console
docker compose up --build
```
Эта команда соберёт образ и запустит три контейнера (API, Celery worker и Celery Beat) (для фонового режима добавьте в команду флаг `-d`).
При старте API автоматически применяет миграции (`alembic upgrade head`).

Swagger UI будет доступен по адресу <http://127.0.0.1:8008/docs> (порт `8008` указан в `docker-compose.yml`).

Загруженные изображения сохраняются в папку `src/static/images` на вашем компьютере.

#### Остановка
Остановить контейнеры приложения:

```console
docker compose stop
```
Остановить и удалить контейнеры приложения:
```console
docker compose down
```

### Запуск без Docker

В этом варианте API, PostgreSQL и Redis запускаются напрямую на вашем компьютере, без контейнеров.

#### 1. Создайте виртуальное окружение и активируйте его

Нужен Python 3.13 (см. `.python-version`).

macOS и Linux:
```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Windows:
```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
```

После активации в начале строки терминала появится `(.venv)`.

#### 2. Установите зависимости

```console
pip install -r requirements.txt
```

#### 3. Установите и запустите PostgreSQL и Redis

PostgreSQL обязателен для работы API. Redis нужен для Celery worker, Celery Beat и
общего кэша между процессами. Без Redis само API запустится и будет использовать
кэш в памяти процесса, но фоновые задачи работать не будут.

В этом варианте PostgreSQL и Redis работают на вашем компьютере на стандартных портах
`5432` и `6379`.

Установка Redis:

macOS:
```bash
brew install redis
brew services start redis
```

Linux: следуйте [официальной инструкции Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/).

Windows: у Redis нет официальной нативной версии для Windows. Установить его можно в WSL или Docker.

Установка PostgreSQL:

macOS:
```bash
brew install postgresql@17
brew services start postgresql@17
```

Linux: выберите PostgreSQL 17 в [официальной инструкции](https://www.postgresql.org/download/linux/).

Windows: скачайте установщик PostgreSQL 17 с [официального сайта](https://www.postgresql.org/download/windows/). Во время установки запомните пароль пользователя `postgres` и оставьте порт `5432`, если он не занят.

После установки PostgreSQL откройте его консоль:

macOS:
```bash
psql postgres
```

Linux:
```bash
sudo -u postgres psql
```

Windows: откройте приложение SQL Shell (psql) из меню «Пуск» и подключитесь к базе `postgres` от имени пользователя `postgres`. Если `psql` добавлен в `PATH`, можно выполнить:
```powershell
psql -U postgres -d postgres
```

Создайте отдельного пользователя и базу данных. Вместо `change-me` задайте собственный пароль:
```sql
CREATE USER booking_user WITH PASSWORD 'change-me';
CREATE DATABASE booking OWNER booking_user;
```

#### 4. Проверьте `.env`

Значения в `.env` должны совпадать с созданными пользователем, паролем и базой:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_USER=booking_user
DB_PASS=change-me
DB_NAME=booking

REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 5. Примените миграции

PostgreSQL должен быть запущен.
Команду выполняйте из корня проекта с активным виртуальным окружением.
Команда создаст в базе все таблицы:
```console
alembic upgrade head
```

#### 6. Запустите приложение

macOS и Linux:
```bash
make run
```
Команда запускает сервер с флагом `--reload`: при изменении кода он перезапускается сам.
Или (без автоперезапуска):
```bash
PYTHONPATH=src uvicorn src.main:app
```

Windows:
```powershell
$env:PYTHONPATH = "src"
uvicorn src.main:app
```

После запуска доступны:

- Базовый URL API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

В Swagger UI можно посмотреть все эндпоинты, их параметры и отправить тестовые запросы из браузера.

#### Фоновые задачи Celery

Celery нужен для двух задач:
- worker создаёт уменьшенные копии загруженных изображений и отправляет письма;
- Celery Beat каждый день в 01:00 UTC ставит в очередь задачу рассылки напоминаний о заезде.
  Для отправки писем нужны рабочие `SMTP_*` настройки в `.env`.

Для рассылки напоминаний должны одновременно работать worker и Beat.
Redis должен быть запущен до их старта.
Каждую команду запускайте в отдельном терминале из корня проекта с активным виртуальным окружением.

- Celery Worker:
    ```bash
    make worker
    ```
    или
    ```bash
    PYTHONPATH=src celery --app=tasks.celery_app:celery_instance worker --loglevel=INFO
    ```

    Windows:
    ```powershell
    $env:PYTHONPATH = "src"
    celery --app=tasks.celery_app:celery_instance worker --loglevel=INFO --pool=solo
    ```

- Celery Beat:
    ```bash
    make beat
    ```
    или
    ```bash
    PYTHONPATH=src celery --app=tasks.celery_app:celery_instance beat --loglevel=INFO
    ```

    Windows:
    ```powershell
    $env:PYTHONPATH = "src"
    celery --app=tasks.celery_app:celery_instance beat --loglevel=INFO
    ```

## Тесты

Тесты при запуске удаляют и заново создают все таблицы, поэтому для них нужна **отдельная
тестовая база**. Не запускайте тесты на рабочей базе `booking`: данные в ней будут потеряны.

Для тестов нужен только запущенный PostgreSQL. Redis и почтовый сервер не нужны: кэш и Celery-задачи заменены заглушками. `pytest` запускается на вашем компьютере, поэтому PostgreSQL должен быть доступен через `localhost`.

### 1. Создайте тестовую базу `booking_test`

Если используете Docker:

Запустите контейнер с тестовой базой

macOS и Linux:
```bash
docker run -d --name booking-db-test \
  -p 6433:5432 \
  -e POSTGRES_USER=booking_user \
  -e POSTGRES_PASSWORD=change-me \
  -e POSTGRES_DB=booking_test \
  postgres:17
```

Windows:
```powershell
docker run -d --name booking-db-test `
  -p 6433:5432 `
  -e POSTGRES_USER=booking_user `
  -e POSTGRES_PASSWORD=change-me `
  -e POSTGRES_DB=booking_test `
  postgres:17
```

Если PostgreSQL установлен локально, создайте в нем отдельную базу данных. Откройте `psql` от имени администратора PostgreSQL:

macOS:
```bash
psql postgres
```

Linux:
```bash
sudo -u postgres psql
```

Windows: SQL Shell (psql), если `psql` добавлен в `PATH`:
```powershell
psql -U postgres -d postgres
```

Затем в консоли выполните SQL-команду:
```sql
CREATE DATABASE booking_test OWNER booking_user;
```

### 2. Настройте `.env-test`

macOS и Linux:
```bash
cp .env-example .env-test
```

Windows:
```powershell
copy .env-example .env-test
```

Если создавали контейнер, измените переменные в `.env-test`:
```dotenv
MODE=TEST
DB_HOST=localhost
DB_PORT=6433
DB_USER=booking_user
DB_PASS=change-me
DB_NAME=booking_test
```

Для локального PostgreSQL используйте `DB_PORT=5432`. Значения `DB_USER` и `DB_PASS`
должны совпадать с учётными данными PostgreSQL, а `DB_NAME` должен оставаться
`booking_test`.

Остальные переменные можно не менять. Если `MODE` не равен `TEST`, тесты остановятся
до очистки базы.

### 3. Запустите тесты

Из корня проекта с активным виртуальным окружением:

```console
pytest                          # все тесты
pytest tests/unit_tests         # только юнит-тесты
pytest tests/integration_tests  # только интеграционные тесты
pytest -v -k booking            # подробный вывод, только тесты со словом booking в названии
```

## Ограничения проекта
- Проект учебный: роли пользователей не реализованы.
- Авторизация требуется только для `GET /auth/me`, `POST /auth/logout`, `POST /bookings`, `GET /bookings/me` и `DELETE /bookings/{booking_id}`. Создание, изменение и удаление отелей и номеров, создание и удаление удобств, просмотр всех бронирований (`GET /bookings`) и загрузка файлов сейчас не требуют аутентификации или прав администратора.
- В `docker-compose.yml` входят только API, Celery worker и Celery Beat. PostgreSQL, Redis и внешнюю Docker-сеть необходимо подготовить отдельно.
- Отправка писем зависит от внешнего SMTP-сервера; повторные попытки доставки не настроены.
- Проверка доступности и создание бронирования выполняются без блокировки, поэтому конкурентные запросы могут привести к превышению доступного количества номеров.

## Как работать с API

Удобнее всего начать со Swagger UI:

1. Выполните `POST /auth/register`, чтобы зарегистрироваться (email и пароль).
2. Выполните `POST /auth/login`. Сервер сохранит JWT в cookie `access_token`, и Swagger UI будет автоматически отправлять его в следующих запросах.
Проверить вход можно через `GET /auth/me`.
3. Создайте удобства (`POST /facilities`), отель (`POST /hotels`) и номера отеля (`POST /hotels/{hotel_id}/rooms`).
4. Найдите свободные отели (`GET /hotels`) или номера отеля (`GET /hotels/{hotel_id}/rooms`) на нужные даты: параметры `date_from` и `date_to` обязательны.
5. Выполните `POST /bookings` с `room_id`, `date_from` и `date_to`, чтобы создать бронирование.
Свои бронирования можно посмотреть через `GET /bookings/me`, удалить бронирование — через `DELETE /bookings/{booking_id}`.
6. Для загрузки изображения используйте `POST /images`. Для создания уменьшенных копий должны быть запущены Redis и Celery worker.
7. Выйти из аккаунта можно через `POST /auth/logout`.
