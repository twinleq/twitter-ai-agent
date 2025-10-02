# 🚀 Быстрый старт AI Twitter Agent

Краткое руководство для немедленного запуска вашего AI Twitter бота.

## ⚡ За 5 минут

### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

### 2. Настройте конфигурацию
```bash
copy config.env.example .env
```

Отредактируйте `.env` файл:
```env
TWITTER_API_KEY=ваш_ключ
TWITTER_API_SECRET=ваш_секрет
TWITTER_ACCESS_TOKEN=ваш_токен
TWITTER_ACCESS_TOKEN_SECRET=ваш_секрет_токена
TWITTER_BEARER_TOKEN=ваш_медвежий_токен
OPENAI_API_KEY=ваш_openai_ключ
BOT_USERNAME=ваш_username
```

### 3. Протестируйте
```bash
python test_bot.py
```

### 4. Запустите бота
```bash
python main.py
```

## 🎯 Основные команды

```bash
# Создать пост
python cli.py post --topic programming

# Создать тред
python cli.py post --topic ai --thread 3

# Планировать пост
python cli.py schedule --add "Мой пост" --time "2024-01-15 10:00"

# Посмотреть аналитику
python cli.py analytics --days 7

# Проверить конфигурацию
python cli.py config --validate
```

## 🔧 Быстрые настройки

### Изменить время постинга
В `.env` файле:
```env
POSTING_SCHEDULE_HOUR=14  # 14:00
POSTING_SCHEDULE_MINUTE=30  # 14:30
```

### Изменить количество постов в день
```env
MAX_POSTS_PER_DAY=3  # Максимум 3 поста в день
```

### Изменить темы
```env
POST_THEMES=programming,ai,devops,security
```

### Отключить автоответы
```env
RESPONSE_ENABLED=false
```

## 🛡 Безопасность

**ВАЖНО:** Начните с тестового режима!

```bash
# Сначала тестируйте без публикации
python cli.py post --topic programming --dry-run

# Проверяйте конфигурацию
python cli.py config --test-api
```

## 📊 Мониторинг

```bash
# Посмотреть логи
type logs\twitter_agent.log

# Посмотреть статистику
python cli.py analytics --days 1

# Создать резервную копию
python cli.py utils --backup
```

## 🆘 Если что-то не работает

1. **Проверьте API ключи** - они должны быть правильными
2. **Запустите тесты** - `python test_bot.py`
3. **Проверьте логи** - `type logs\twitter_agent.log`
4. **Убедитесь в интернет-соединении**

## 🎉 Готово!

Ваш AI Twitter Agent готов к работе! 

- 🤖 Автоматически генерирует посты
- 📅 Публикует по расписанию  
- 💬 Отвечает на сообщения
- 📊 Собирает аналитику

**Удачи с развитием вашей социальной сети!** 🚀
