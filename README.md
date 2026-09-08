# Блог на Django 🚀

Современный блог, написанный на **Django 6** с поддержкой Markdown, асинхронной отправкой писем через **Celery**, тегированием и полнотекстовым/триграммным поиском на базе **PostgreSQL**.

---

## ⭐️ Основные возможности

* 📝 **Публикация постов**:
  * Статусы статей (черновик / опубликовано).
  * ЧПУ (URL с датой и слагом): `/blog/2026/8/12/my-first-post/`.
  * Разметка **Markdown** в теле статей с безопасной фильтрацией HTML через `nh3`.

* 🏷 **Тегирование и рекомендации**:
  * Категоризация статей по тегам (`django-taggit`).
  * Фильтрация статей по тегу (`/blog/tag/<tag_slug>/`).
  * Автоматический подбор **похожих статей** на основе общих тегов.

* 💬 **Комментарии**:
  * Добавление комментариев к статьям и модерация (`active=True/False`).
  * Обработка ошибок валидации формы прямо на странице статьи.

* ⚡️ **Асинхронные задачи (Celery + Redis)**:
  * Отправка постов по e-mail вынесена в фоновые задачи **Celery**.

* 🔍 **Умный поиск (PostgreSQL)**:
  * Двухуровневый поиск: полнотекстовый поиск (`SearchVector`, `SearchRank`) с фоллбэком на триграммный поиск (`TrigramSimilarity`).

* 📡 **SEO & Синодация**:
  * XML-карта сайта (`/sitemap.xml`).
  * RSS-канал для подписчиков (`/blog/feed/`).

---

## 🛠 Технологический стек

* **Бэкенд:** Python 3.12+, Django 6.0.6
* **База данных:** PostgreSQL 16 (`pg_trgm`)
* **Фоновые задачи:** Celery 5.6+, Redis 7+
* **Работа с Markdown & HTML:** `markdown`, `nh3`
* **Конфигурация:** `django-environ`, разделение настроек (`dev.py` / `prod.py`)

---

## 📂 Структура маршрутов (URL)

| URL | Название маршрута | Описание |
| :--- | :--- | :--- |
| `/blog/` | `blog:post_list` | Главная страница блога (список опубликованных постов) |
| `/blog/tag/<slug>/` | `blog:post_list_by_tag` | Фильтрация постов по тегу |
| `/blog/<year>/<month>/<day>/<slug>/` | `blog:post_detail` | Страница конкретного поста |
| `/blog/<post_id>/share/` | `blog:post_share` | Форма отправки поста по e-mail |
| `/blog/<post_id>/comment/` | `blog:post_comment` | Добавление комментария (POST) |
| `/blog/feed/` | `blog:post_feed` | RSS-лента последних постов |
| `/blog/search/` | `blog:post_search` | Поиск по статьям |
| `/sitemap.xml` | `sitemap` | Карта сайта XML |
| `/admin/` | — | Панель администратора Django |

---

## 🚀 Запуск и настройка проекта

### Вариант 1: Запуск через Docker Compose (Рекомендуется)

1. **Скопируйте конфигурацию переменных окружения**:
   ```bash
   cp env.example .env
   ```

2. **Запустите контейнеры**:
   ```bash
   docker compose up -d --build
   ```

3. **Примените миграции и создайте суперпользователя**:
   ```bash
   docker compose exec web python mysite/manage.py migrate
   docker compose exec web python mysite/manage.py createsuperuser
   ```

4. **Проверьте запущенные сервисы и логи**:
   ```bash
   docker compose ps
   docker compose logs -f web
   docker compose logs -f worker
   ```

Сайт доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

### Вариант 2: Локальный запуск без Docker

#### 1. Установка зависимостей
```bash
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

#### 2. Переменные окружения (`.env`)
Создайте файл `.env` в корне репозитория (`blog_app/.env`):
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@localhost:5432/blog
CELERY_BROKER_URL=redis://localhost:6379/0
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### 3. Миграции и запуск

> **Важно:** Все команды управления Django и Celery выполняются с указанием рабочей директории `mysite`.

Применение миграций:
```bash
python mysite/manage.py migrate
python mysite/manage.py createsuperuser
```

Запуск сервера разработки:
```bash
python mysite/manage.py runserver
```

Запуск воркера Celery (в отдельном терминале):
```bash
# Вариант A: перейдя в папку mysite
cd mysite
celery -A mysite worker --loglevel=info

# Вариант B: из корня репозитория
celery -A mysite --workdir=mysite worker --loglevel=info
```

---

## 🐳 CI/CD и Docker Hub

Проект содержит GitHub Actions workflow (`.github/workflows/ci-cd.yml`):
* Автоматический прогон тегов и Django-тестов в Docker при пуше в `main`/`master` или PR.
* Сборка и публикация образа в Docker Hub: `kayrattad/django-blog:latest`.

---

## 🧪 Запуск тестов

Выполнение unit-тестов проекта:
```bash
python mysite/manage.py test blog
```

Запуск тестов в Docker-окружении:
```bash
docker compose run --rm web python mysite/manage.py test blog
```
