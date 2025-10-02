# AI Twitter Agent 🤖

Автоматический AI-агент для ведения Twitter аккаунта с возможностью генерации постов, ответов на сообщения и аналитики.

## 🚀 Возможности

- **Автоматическая генерация постов** с помощью OpenAI GPT
- **Планирование публикаций** по расписанию
- **Автоматические ответы** на упоминания и прямые сообщения
- **Аналитика и метрики** производительности
- **Поддержка тредов** (несколько связанных твитов)
- **Система фильтрации спама** и нежелательного контента
- **Многоязычная поддержка** (русский/английский)

## 📋 Требования

- Python 3.8+
- Twitter Developer Account
- OpenAI API Key

## 🛠 Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd Ai\ agent
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**
```bash
cp config.env.example .env
```

4. **Заполните файл .env:**
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

## 🚀 Запуск

```bash
python main.py
```

## ⚙️ Конфигурация

### Основные настройки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `AUTO_POSTING_ENABLED` | Автоматическая публикация постов | `true` |
| `POSTING_SCHEDULE_HOUR` | Час публикации | `9` |
| `POSTING_SCHEDULE_MINUTE` | Минута публикации | `0` |
| `MAX_POSTS_PER_DAY` | Максимум постов в день | `5` |
| `RESPONSE_ENABLED` | Автоответы на сообщения | `true` |
| `CONTENT_LANGUAGE` | Язык контента (`ru`/`en`) | `ru` |

### Темы для постов

Настройте темы в параметре `POST_THEMES`:
```env
POST_THEMES=technology,programming,ai,devops,automation,security,cloud
```

### Расписание постов

Бот автоматически распределяет посты в течение дня между 9:00 и 21:00, учитывая параметр `MAX_POSTS_PER_DAY`.

## 📊 Аналитика

Система автоматически собирает метрики:

- **Вовлеченность постов** (лайки, ретвиты, ответы)
- **Статистика ответов** на сообщения
- **Ежедневная активность**
- **Топ темы** по популярности
- **Метрики пользователей**

### Просмотр аналитики

Аналитика сохраняется в SQLite базе данных (`./data/analytics.db`) и обновляется автоматически.

## 🔧 API

### Основные классы

- `TwitterClient` - работа с Twitter API
- `AIContentGenerator` - генерация контента с помощью AI
- `PostScheduler` - планирование и публикация постов
- `MessageHandler` - обработка сообщений и ответов
- `Analytics` - сбор и анализ метрики

### Пример использования

```python
from src.config import Config
from src.twitter_client import TwitterClient
from src.ai_content_generator import AIContentGenerator

# Инициализация
config = Config()
twitter_client = TwitterClient(config)
ai_generator = AIContentGenerator(config)

# Генерация и публикация поста
post = ai_generator.generate_post(topic="programming")
tweet_id = twitter_client.post_tweet(post)
```

## 🛡 Безопасность

- **Фильтрация спама** - автоматическое определение нежелательного контента
- **Черный список** - настраиваемый список запрещенных слов
- **Лимиты ответов** - ограничение на количество ответов одному пользователю
- **Валидация контента** - проверка длины твитов и корректности

## 📝 Логирование

Логи сохраняются в папке `./logs/`:
- `twitter_agent.log` - основные логи работы
- Уровни логирования: DEBUG, INFO, WARNING, ERROR

## 🔄 Резервное копирование

Система автоматически создает резервные копии:
- Расписания постов
- Истории публикаций
- Настроек конфигурации

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибка подключения к Twitter API**
   - Проверьте правильность API ключей
   - Убедитесь, что у аккаунта есть необходимые права

2. **Ошибка OpenAI API**
   - Проверьте API ключ OpenAI
   - Убедитесь в наличии средств на счету

3. **Проблемы с публикацией**
   - Проверьте лимиты Twitter API
   - Убедитесь, что контент соответствует правилам платформы

### Логи

Проверьте логи в файле `./logs/twitter_agent.log` для диагностики проблем.

## 📈 Мониторинг

Рекомендуется мониторить:
- Количество опубликованных постов
- Уровень вовлеченности
- Ошибки в логах
- Использование API лимитов

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь в корректности конфигурации
3. Проверьте статус API сервисов

## 📄 Лицензия

MIT License

## 🔮 Планы развития

- [ ] Веб-интерфейс для управления
- [ ] Поддержка других социальных сетей
- [ ] Расширенная аналитика с графиками
- [ ] Интеграция с внешними сервисами
- [ ] A/B тестирование постов
