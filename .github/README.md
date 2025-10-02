# 🤖 AI Twitter Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-orange.svg)](https://openai.com)

Автоматический AI-агент для ведения Twitter аккаунта с возможностью генерации постов, ответов на сообщения и аналитики.

## ✨ Возможности

- 🤖 **Автоматическая генерация постов** с помощью OpenAI GPT
- 📅 **Планирование публикаций** по расписанию
- 💬 **Автоматические ответы** на упоминания и прямые сообщения
- 📊 **Аналитика и метрики** производительности
- 🧵 **Поддержка тредов** (несколько связанных твитов)
- 🛡️ **Система фильтрации спама** и нежелательного контента
- 🌐 **Многоязычная поддержка** (русский/английский)
- 📱 **CLI интерфейс** для управления

## 🚀 Быстрый старт

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/twinleq/twitter-ai-agent.git
cd twitter-ai-agent
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте конфигурацию:**
```bash
cp config.env.example .env
# Отредактируйте .env файл с вашими API ключами
```

4. **Протестируйте:**
```bash
python test_bot.py
```

5. **Запустите:**
```bash
python main.py
```

## 📋 Требования

- Python 3.8+
- Twitter Developer Account
- OpenAI API Key

## 📖 Документация

- [📖 Полная документация](README.md)
- [🛠 Руководство по установке](INSTALL.md)
- [⚡ Быстрый старт](QUICKSTART.md)
- [🏗 Архитектура](ARCHITECTURE.md)

## 🎯 Основные команды

```bash
# Запуск бота
python main.py

# Создание поста
python cli.py post --topic programming

# Планирование поста
python cli.py schedule --add "Мой пост" --time "2024-01-15 10:00"

# Аналитика
python cli.py analytics --days 7
```

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста, ознакомьтесь с нашими [правилами контрибьюции](CONTRIBUTING.md).

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [OpenAI](https://openai.com) за API для генерации контента
- [Tweepy](https://github.com/tweepy/tweepy) за Twitter API клиент
- Всем контрибьюторам проекта

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [документацию](README.md)
2. Посмотрите [существующие issues](https://github.com/twinleq/twitter-ai-agent/issues)
3. Создайте [новый issue](https://github.com/twinleq/twitter-ai-agent/issues/new)

---

⭐ **Если проект вам понравился, поставьте звезду!** ⭐
