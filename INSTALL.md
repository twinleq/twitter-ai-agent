# 🚀 Установка AI Twitter Agent

Пошаговая инструкция по установке и настройке AI Twitter Agent.

## 📋 Предварительные требования

### 1. Python 3.8+
Убедитесь, что у вас установлен Python 3.8 или новее:
```bash
python --version
```

### 2. Twitter Developer Account
1. Перейдите на [developer.twitter.com](https://developer.twitter.com)
2. Создайте аккаунт разработчика
3. Создайте новое приложение (App)
4. Получите следующие ключи:
   - API Key
   - API Secret Key
   - Access Token
   - Access Token Secret
   - Bearer Token

### 3. OpenAI API Key
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Создайте аккаунт
3. Получите API ключ в разделе API Keys

## 🛠 Установка

### Шаг 1: Клонирование проекта
```bash
cd "Ai agent"
```

### Шаг 2: Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 3: Настройка конфигурации
```bash
# Копируем пример конфигурации
copy config.env.example .env

# Редактируем файл .env
notepad .env
```

### Шаг 4: Заполнение конфигурации
Откройте файл `.env` и заполните следующие поля:

```env
# Twitter API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Bot Configuration
BOT_USERNAME=your_twitter_username
POSTING_SCHEDULE_HOUR=9
POSTING_SCHEDULE_MINUTE=0
MAX_POSTS_PER_DAY=5
RESPONSE_ENABLED=true
AUTO_RESPONSE_ENABLED=false

# Content Settings
CONTENT_LANGUAGE=ru
POST_THEMES=technology,programming,ai,devops,automation
HASHTAG_COUNT=3
MENTION_FOLLOWERS=false

# Analytics
ENABLE_ANALYTICS=true
ANALYTICS_DB_PATH=./data/analytics.db
```

## 🧪 Тестирование

### Быстрое тестирование
```bash
python test_bot.py
```

### Тестирование отдельных компонентов
```bash
# Тест конфигурации
python test_bot.py config

# Тест Twitter API
python test_bot.py twitter

# Тест OpenAI API
python test_bot.py openai

# Тест генерации контента
python test_bot.py content
```

## 🚀 Запуск

### Основной запуск
```bash
python main.py
```

### Запуск через CLI
```bash
# Запуск бота
python cli.py run

# Создание поста
python cli.py post --topic programming

# Планирование поста
python cli.py schedule --add "Мой пост" --time "2024-01-15 10:00"

# Просмотр аналитики
python cli.py analytics --days 7
```

## ⚙️ Настройка

### Основные параметры

| Параметр | Описание | Рекомендуемое значение |
|----------|----------|------------------------|
| `POSTING_SCHEDULE_HOUR` | Час основного поста | 9 (9:00 утра) |
| `MAX_POSTS_PER_DAY` | Максимум постов в день | 3-5 |
| `CONTENT_LANGUAGE` | Язык контента | `ru` или `en` |
| `RESPONSE_ENABLED` | Автоответы | `true` |
| `AUTO_RESPONSE_ENABLED` | Автоматические ответы | `false` (для безопасности) |

### Темы для контента
Настройте темы в `POST_THEMES`:
```env
POST_THEMES=technology,programming,ai,devops,automation,security,cloud,data
```

### Расписание постов
Бот автоматически распределяет посты в течение дня:
- Основной пост в указанное время
- Дополнительные посты равномерно между 9:00 и 21:00

## 🔧 Управление

### CLI команды

```bash
# Запуск бота
python cli.py run

# Создание поста
python cli.py post --topic ai --dry-run

# Создание треда
python cli.py post --topic programming --thread 3

# Планирование
python cli.py schedule --list
python cli.py schedule --add "Текст поста" --time "2024-01-15 14:30"

# Аналитика
python cli.py analytics --days 30
python cli.py analytics --export report.json

# Ответы
python cli.py response --stats
python cli.py response --reply 1234567890 --text "Спасибо!"

# Конфигурация
python cli.py config --show
python cli.py config --validate
python cli.py config --test-api

# Утилиты
python cli.py utils --backup
python cli.py utils --clean
```

### Примеры использования
```bash
# Запуск примеров
python examples.py

# Конкретный пример
python examples.py post
python examples.py thread
python examples.py analytics
```

## 📊 Мониторинг

### Логи
Логи сохраняются в папке `./logs/`:
- `twitter_agent.log` - основные логи
- Уровни: DEBUG, INFO, WARNING, ERROR

### Аналитика
Данные сохраняются в SQLite базе `./data/analytics.db`:
- Метрики постов
- Статистика ответов
- Ежедневная активность
- Метрики пользователей

### Резервные копии
```bash
# Создание резервной копии
python cli.py utils --backup

# Восстановление
python cli.py utils --restore backup_20240115_143022
```

## 🛡 Безопасность

### Рекомендации
1. **Не публикуйте API ключи** в открытом доступе
2. **Используйте тестовый режим** сначала
3. **Настройте фильтры** для спама
4. **Ограничьте частоту** постинга
5. **Мониторьте логи** на ошибки

### Настройки безопасности
```env
# Ограничения
MAX_POSTS_PER_DAY=3
RESPONSE_ENABLED=true
AUTO_RESPONSE_ENABLED=false

# Фильтрация
BLACKLISTED_WORDS=spam,scam,fake
MAX_FOLLOWERS_TO_MENTION=10
```

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибка "Invalid credentials"**
   - Проверьте правильность API ключей Twitter
   - Убедитесь, что у приложения есть необходимые права

2. **Ошибка "OpenAI API"**
   - Проверьте API ключ OpenAI
   - Убедитесь в наличии средств на счету

3. **Ошибка "Rate limit exceeded"**
   - Уменьшите `MAX_POSTS_PER_DAY`
   - Увеличьте интервалы между постами

4. **Ошибка "Tweet too long"**
   - Уменьшите `HASHTAG_COUNT`
   - Проверьте `MAX_TWEET_LENGTH`

### Диагностика
```bash
# Проверка конфигурации
python cli.py config --validate

# Тест API
python cli.py config --test-api

# Полное тестирование
python test_bot.py
```

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте логи** в `./logs/twitter_agent.log`
2. **Запустите тесты** с `python test_bot.py`
3. **Проверьте конфигурацию** с `python cli.py config --validate`
4. **Убедитесь в доступности** API сервисов

## 🎯 Следующие шаги

После успешной установки:

1. **Настройте темы** контента под вашу нишу
2. **Определите оптимальное** время постинга
3. **Протестируйте автоответы** в безопасном режиме
4. **Настройте мониторинг** и аналитику
5. **Создайте резервные копии** конфигурации

Удачи с вашим AI Twitter Agent! 🚀
