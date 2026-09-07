# Блог на Django 🚀

Современный, производительный и полнофункциональный блог, написанный на **Django 6** с поддержкой Markdown, асинхронной отправкой писем через **Celery**, тегированием и умным поиском на базе **PostgreSQL**.

---

## ⭐️ Основные возможности

* 📝 **Публикация постов**:
  * Поддержка статусов статей (черновик / опубликовано).
  * ЧПУ (Человекопонятные URL) с датой и слагом: `/blog/2026/8/12/my-first-post/`.
  * Разметка **Markdown** в теле статей с безопасной компиляцией в HTML.

* 🏷 **Тегирование и рекомендации**:
  * Категоризация статей по тегам (`django-taggit`).
  * Фильтрация статей по выбранному тегу (`/blog/tag/python/`).
  * Автоматический подбор **похожих статей** на основе общих тегов.

* 💬 **Комментарии**:
  * Добавление комментариев к статьям.
  * Система модерации (активные / скрытые комментарии).
  * Корректная обработка ошибок формы прямо на странице статьи.

* ⚡️ **Асинхронные задачи (Celery)**:
  * Возможность "поделиться статьёй по E-mail".
  * Отправка писем вынесена в фоновые задачи **Celery**, чтобы сайт работал мгновенно и не заставлял пользователя ждать ответа SMTP-сервера.

* 🔍 **Умный поиск (PostgreSQL)**:
  * Двухуровневый поиск: полнотекстовый поиск по заголовку и тексту с ранжированием результатов (`SearchVector`, `SearchRank`).
  * Автоматический фоллбэк на поиск по сходству триграмм (`TrigramSimilarity`), если точных совпадений не найдено (спасёт при опечатках).

* 📡 **SEO & Синодация**:
  * Автоматическая генерация XML-карты сайта (`/sitemap.xml`).
  * Полноценный RSS-канал для подписчиков (`/blog/feed/`).

---

## 🛠 Технологический стек

* **Бэкенд:** Python 3.12+, Django 6.0
* **База данных:** PostgreSQL (полнотекстовый поиск + модуль `pg_trgm` для триграммного поиска)
* **Фоновые задачи:** Celery + Redis
* **Работа с Markdown:** `markdown`
* **Оптимизация ORM:** `select_related`, `prefetch_related` (защита от N+1)
* **Конфигурация:** `django-environ`, разделение настроек (`dev.py` / `prod.py`)

---

## 🚀 Запуск и настройка проекта

### Основной способ: Запуск через Docker Compose (Рекомендуется)

Самый быстрый способ запустить приложение вместе с PostgreSQL и Redis:

1. Скопируйте пример переменных окружения в корень проекта (`.env`):
   ```bash
   cp env.example .env
   ```
2. Запустите контейнеры в фоновом режиме:
   ```bash
   docker compose up -d --build
   ```
3. Проверьте статус запущенных контейнеров:
   ```bash
   docker compose ps
   ```
4. Выполните миграции и создайте суперпользователя:
   ```bash
   docker compose exec web python mysite/manage.py migrate
   docker compose exec web python mysite/manage.py createsuperuser
   ```

**Команды для управления Docker Compose:**
* Просмотр логов веб-приложения:
  ```bash
  docker compose logs web
  ```
* Просмотр логов Celery воркера:
  ```bash
  docker compose logs worker
  ```
* Остановка контейнеров:
  ```bash
  docker compose down
  ```

Сайт будет доступен по адресу: [http://127.0.0.1:8000/blog/](http://127.0.0.1:8000/blog/)

---

### Альтернативный способ: Локальный запуск (без Docker)

#### 1. Установка зависимостей
Из корневой директории проекта:
```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Переменные окружения (`.env`)
Создайте файл `.env` в **корне репозитория** (не внутри папки `mysite`):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/blog_db
CELERY_BROKER_URL=redis://localhost:6379/0
```

#### 3. Миграции и запуск
```bash
python mysite/manage.py migrate
python mysite/manage.py createsuperuser
```

В одном терминале запустите сервер разработки:
```bash
python mysite/manage.py runserver
```

В другом терминале запустите воркер Celery:
```bash
celery -A mysite.celery worker --loglevel=info
```

---

## 🐳 Docker Hub & CI/CD

### CI/CD Pipeline
Проект настроен с использованием GitHub Actions (`.github/workflows/ci-cd.yml`):
* **Git push / Pull Request** → Запуск тегов/тестов в Docker → Сборка Docker image → Публикация в Docker Hub.

### Docker Hub Image
* **Образ:** `kayrattad/django-blog:latest`

> **Важно:** Команда `docker pull kayrattad/django-blog:latest` сама по себе не запускает полностью готовое приложение, так как веб-приложение зависит от работающей базы данных PostgreSQL, брокера Redis и правильно настроенных переменных окружения (например, через `docker-compose.yml`).

---

## 📂 Структура проекта

```text
blog_app/
├── .github/workflows/      # CI/CD пайплайны GitHub Actions
├── mysite/                 # Корневой каталог Django
│   ├── blog/               # Основное приложение блога
│   │   ├── templatetags/   # Кастомные теги и фильтры (Markdown, последние посты)
│   │   ├── templates/      # HTML-шаблоны сайта
│   │   ├── admin.py        # Настройки админ-панели
│   │   ├── feeds.py        # RSS-лента
│   │   ├── models.py       # Модели Post и Comment
│   │   ├── sitemaps.py     # Генерация sitemap.xml
│   │   ├── tasks.py        # Асинхронные задачи Celery
│   │   ├── urls.py         # Маршруты блога
│   │   └── views.py        # Представления (Class-Based Views)
│   ├── mysite/             # Пакет конфигурации проекта
│   │   ├── settings/       # Настройки (base.py, dev.py, prod.py)
│   │   ├── celery.py       # Конфигурация Celery
│   │   └── urls.py         # Главные маршруты
│   └── manage.py
├── Dockerfile
├── docker-compose.yml
├── env.example
└── requirements.txt
```
