# Контакты: Django + XML + PostgreSQL + Docker

```markdown
# Контакты — Django + XML + PostgreSQL + Docker

Полноценное веб-приложение для управления контактами с поддержкой двух источников хранения:  
единый XML-файл (`media/contacts.xml`) и PostgreSQL.  
Всё упаковано в Docker, готово к деплою одной командой.

## Функционал
- Добавление контакта → выбор: XML-файл или База данных
- Загрузка любого корректного XML → контакты добавляются в общий `media/contacts.xml`
- Просмотр контактов с мгновенным переключением источника (XML / БД)
- AJAX-поиск по имени, фамилии, email и телефону (только для БД)
- Редактирование и удаление записей (только для БД)
- Строгая валидация на всех уровнях
- Проверка дубликатов в БД
- Адаптивный интерфейс на Bootstrap 5

## Технологии
- Django 5.1+
- PostgreSQL 15
- Gunicorn
- Docker + Docker Compose
- pgloader (миграция SQLite → PostgreSQL)
- Bootstrap 5 + jQuery

## Структура проекта
```
contactsProject/
├── contacts/                  # настройки проекта
├── contactsXML/               # основное приложение
├── media/contacts.xml         # единый XML-файл
├── .env                       # ← НЕ в Git!
├── .env.example
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py

## Полные инструкции по запуску

### 1. Создание .env

### Генерация SECRET_KEY
```bash
# Выполни в терминале — получишь надёжный ключ
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Скопируй результат и замени строку `SECRET_KEY=...` в файле `.env`.


```bash
cp .env.example .env
```
Отредактируй `.env`:
```env
DEBUG=False
SECRET_KEY=твой_очень_длинный_ключ_из_предыдущей_команды
ALLOWED_HOSTS=*

POSTGRES_DB=contacts_db
POSTGRES_USER=contacts_user
POSTGRES_PASSWORD=очень_надёжный_пароль_12345
```

### 2. Запуск проекта
```bash
docker compose up --build          # первый раз 
docker compose up                  # последующие запуски 
```

### 3. Миграция данных из старой SQLite (если есть db.sqlite3)
```bash
# Переносит все контакты из db.sqlite3 в PostgreSQL одной командой
docker compose --profile tools up pgloader
```
После этого можешь удалить `db.sqlite3`.

### 4. Полезные команды
```bash
docker compose down               # остановить
docker compose down -v            # остановить + удалить БД
docker compose logs web           # логи Django
docker compose exec web bash      # зайти в контейнер
docker compose exec db psql -U contacts_user -d contacts_db   # зайти в PostgreSQL
```


## Безопасность
- Все секреты хранятся в `.env` (не попадает в Git)
- `SECRET_KEY` генерируется криптостойким способом
- PostgreSQL с паролем
- Статические файлы собираются через `collectstatic`