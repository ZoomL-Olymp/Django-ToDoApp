# To-Do List Telegram Bot with Django REST Framework

## Описание

Этот проект представляет собой приложение для управления списком задач (To-Do List), реализованное с использованием Telegram-бота и бэкенда на Django REST Framework.  Пользователи могут взаимодействовать с ботом для добавления, просмотра, изменения статуса и удаления задач. Задачи могут быть сгруппированы по категориям, которые пользователи также могут создавать и назначать задачам.  Проект разворачивается с помощью Docker Compose, что обеспечивает легкую переносимость и воспроизводимость окружения.

## Архитектура

Проект состоит из следующих основных компонентов:

*   **Telegram Bot (aiogram):**  Фронтенд приложения, с которым взаимодействуют пользователи.  Бот обрабатывает команды пользователя, отправляет запросы к API, и отображает результаты.  Используется библиотека `aiogram` для асинхронной работы с Telegram Bot API.
*   **Django REST Framework (DRF):**  Бэкенд приложения, предоставляющий REST API для управления задачами и категориями.  DRF обеспечивает сериализацию данных, аутентификацию (с использованием JWT), и CRUD (Create, Read, Update, Delete) операции.
*   **PostgreSQL:**  Реляционная база данных, используемая для хранения информации о пользователях, задачах и категориях.
*   **Redis:**  Брокер сообщений, используемый Celery для управления асинхронными задачами (в данном случае, для отправки уведомлений).
*   **Celery:**  Система управления очередями задач.  Используется для асинхронной отправки уведомлений пользователям о предстоящих задачах.
*   **Docker Compose:**  Инструмент для определения и запуска многоконтейнерных приложений.  Используется для оркестрации всех сервисов (бота, Django, PostgreSQL, Redis, Celery) и обеспечения их взаимодействия.

**Схема взаимодействия:**

1.  Пользователь отправляет команду Telegram-боту (например, `/add` для добавления задачи).
2.  Бот (aiogram) обрабатывает команду, при необходимости используя конечный автомат (FSM) для сбора данных от пользователя (название задачи, описание, срок выполнения, категория).
3.  Бот отправляет запрос к Django REST Framework API (например, `POST /api/tasks/`).
4.  Django REST Framework (DRF) обрабатывает запрос:
    *   Проверяет аутентификацию пользователя (с использованием JWT).
    *   Валидирует данные (с помощью сериализаторов).
    *   Взаимодействует с базой данных (PostgreSQL) для создания, чтения, обновления или удаления данных.
    *   Если необходимо, ставит задачу в очередь Celery (например, для отправки уведомления).
5.  DRF возвращает ответ боту (например, подтверждение успешного создания задачи, список задач, или сообщение об ошибке).
6.  Бот (aiogram) обрабатывает ответ от API и отправляет сообщение пользователю (например, "Задача успешно создана!").
7.  Celery worker (если задача была поставлена в очередь) асинхронно выполняет задачу (например, отправляет уведомление пользователю через Telegram API).

## Требования

*   Docker
*   Docker Compose

## Запуск проекта

1.  **Клонируйте репозиторий:**

    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```
    (Замените `<repository_url>` на URL вашего репозитория, а `<project_directory>` на имя директории проекта.)

2.  **Настройте переменные окружения:**

    *   Создайте файл `.env` в корне проекта (рядом с `manage.py` и `docker-compose.yml`) *только если планируете запускать бота вне docker*.
    *   Добавьте в файл `.env` следующую строку, заменив `your_actual_bot_token` на токен вашего Telegram-бота (полученный от @BotFather):

    ```
    BOT_TOKEN=your_actual_bot_token
    ```
     *   Укажите *реальные* значения для переменных в `docker-compose.yml`.  **Внимание!** В данном тестовом проекте секретные ключи (пароль от базы данных, `SECRET_KEY`) хранятся непосредственно в `docker-compose.yml`.  В *production* окружении так делать **нельзя**.  Используйте более безопасные способы хранения секретов (например, Docker Secrets, HashiCorp Vault, или переменные окружения, установленные на сервере).

3.  **Соберите и запустите Docker-контейнеры:**

    ```bash
    docker-compose up --build -d
    ```

    Эта команда:
    *   `-d`: Запустит контейнеры в фоновом режиме (detached mode).
    *   `--build`:  Соберет Docker-образы перед запуском (необходимо при первом запуске или после изменений в `Dockerfile` или `requirements.txt`).

4. **Создайте суперпользователя Django (необязательно, но рекомендуется):**
    ```bash
        docker-compose exec web python manage.py createsuperuser
    ```
    
5.  **Доступ к приложению:**

    *   **Telegram-бот:**  Найдите вашего бота в Telegram (по имени пользователя, которое вы указали при создании бота у @BotFather) и начните взаимодействие.
    *   **Django Admin:**  Откройте в браузере `http://localhost:8000/admin/` и войдите, используя данные суперпользователя, которые вы создали.
    *   **API:** API доступен по адресу `http://localhost:8000/api/`.

6.  **Остановка:**

    ```bash
    docker-compose down
    ```

    Для *полного удаления* контейнеров, *включая тома с данными* (БД, Redis), используйте `docker-compose down -v`.  Это полезно при разработке, когда вы хотите начать с чистого листа.

## Трудности и решения

В процессе разработки данного проекта я столкнулся с несколькими трудностями, которые удалось успешно решить:

1.  **`ImportError: attempted relative import beyond top-level package`:**  Эта ошибка возникала из-за неправильной структуры импортов в боте, когда я пытался использовать относительные импорты (`..`) за пределами корневого пакета.  Решение: использовать `python -m bot.main` для запуска бота.

2.  **`TypeError: Passing 'parse_mode', ... to Bot initializer is not supported anymore`:**  Ошибка была связана с изменением API библиотеки `aiogram`.  В новых версиях параметры `parse_mode`, `disable_web_page_preview` и `protect_content` передаются не напрямую в конструктор `Bot`, а через объект `DefaultBotProperties`.  Решение: использование `DefaultBotProperties`.

3.  **`ValidationError: ... bot_token ... Field required`:**  Ошибка валидации Pydantic, возникавшая из-за того, что переменная окружения `BOT_TOKEN` не была найдена.  Решение: проверка наличия `.env` файла, корректности синтаксиса, явная загрузка `.env` с помощью `load_dotenv`.

4.  **`django.db.utils.OperationalError: connection to server at "localhost" ... failed: Connection refused`:**  Ошибка подключения Django к PostgreSQL.  Причина: Django пытался подключиться к `localhost`, в то время как PostgreSQL работал в отдельном Docker-контейнере.  Решение: использование имени сервиса (`db`) в качестве хоста в `DATABASE_URL` и настройка сети Docker Compose.

5.  **`django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured`:** Ошибка конфигурации базы данных. Причина: ошибка в `DATABASES` в `settings.py`.

6. **`NameError: name 'router' is not defined`:** Ошибка возникала из-за того, что декоратор `@router.message` использовался до определения самого `router`. Решение: создание экземпляра `Router` в файле `tasks.py` и импорт его в `__init__.py`.

7.  **`UnboundLocalError: local variable 'response' referenced before assignment`:** Ошибка возникала в `api_client.py` при обработке ошибок `aiohttp`.  Решение: явная проверка на ошибки соединения и HTTP-ошибки (`ClientConnectorError`, `ClientResponseError`).

8.  **Циклический импорт:**  Ошибка `ImportError: cannot import name '...' from partially initialized module ... (most likely due to a circular import)` возникала из-за взаимных импортов между модулями.  Решение: использование отложенных импортов (import внутри функций).

9. **PostgreSQL shutdown**: Была обнаружена проблема с базой данных. Решение: Использовать `wait-for-it.sh`
10. **`nc: command not found`:**  Ошибка возникала из-за отсутствия `netcat` в Docker-образе.  Решение: установка `netcat-openbsd` в `Dockerfile`.
11. **Revoke tasks:** Исправлена ошибка с зацикливанием задач Celery.
12. **`DisallowedHost`:** Добавлен `ALLOWED_HOSTS = ['*']`

## Замечание о секретных переменных

Я понимаю важность хранения секретных данных (таких как `SECRET_KEY`, пароли от базы данных, токены API) в безопасном месте.  В данном *тестовом* проекте для упрощения настройки и запуска я использовал переменные среды, заданные *напрямую* в файле `docker-compose.yml`.

**В production-окружении такой подход недопустим!**

Для production следует использовать один из следующих подходов:

*   **Docker Secrets:**  [https://docs.docker.com/engine/swarm/secrets/](https://docs.docker.com/engine/swarm/secrets/)
*   **HashiCorp Vault:**  [https://www.vaultproject.io/](https://www.vaultproject.io/)
*   **Переменные окружения, установленные на сервере:**  Настроить переменные окружения непосредственно на сервере (или в панели управления хостинга), а в `docker-compose.yml` использовать ссылки на них (`${VAR_NAME}`).
* **Kubernates secrets**
