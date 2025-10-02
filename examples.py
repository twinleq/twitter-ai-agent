#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования AI Twitter Agent
Демонстрирует различные возможности бота
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.twitter_client import TwitterClient
from src.ai_content_generator import AIContentGenerator
from src.post_scheduler import PostScheduler
from src.message_handler import MessageHandler
from src.analytics import Analytics

def example_basic_post():
    """Пример создания и публикации обычного поста"""
    print("📝 Пример: Создание обычного поста")
    
    load_dotenv()
    config = Config()
    
    # Инициализируем компоненты
    twitter_client = TwitterClient(config)
    ai_generator = AIContentGenerator(config)
    
    # Генерируем пост на тему программирования
    post = ai_generator.generate_post("programming")
    
    if post:
        print(f"Сгенерированный пост:\n{post}\n")
        
        # Публикуем пост (раскомментируйте для реальной публикации)
        # tweet_id = twitter_client.post_tweet(post)
        # print(f"Пост опубликован с ID: {tweet_id}")
        
        print("✅ Пост готов к публикации")

def example_thread_creation():
    """Пример создания треда"""
    print("🧵 Пример: Создание треда")
    
    load_dotenv()
    config = Config()
    
    ai_generator = AIContentGenerator(config)
    
    # Создаем тред из 3 твитов на тему AI
    thread = ai_generator.generate_thread("artificial intelligence", 3)
    
    if thread:
        print("Сгенерированный тред:")
        for i, tweet in enumerate(thread, 1):
            print(f"\n{i}/{len(thread)}: {tweet}")
        
        print("\n✅ Тред готов к публикации")

def example_scheduled_posting():
    """Пример планирования постов"""
    print("📅 Пример: Планирование постов")
    
    load_dotenv()
    config = Config()
    
    twitter_client = TwitterClient(config)
    ai_generator = AIContentGenerator(config)
    scheduler = PostScheduler(config, twitter_client, ai_generator)
    
    # Планируем пост на завтра в 10:00
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    custom_post = "Запланированный пост про DevOps и автоматизацию! 🚀"
    
    success = scheduler.schedule_custom_post(custom_post, scheduled_time)
    
    if success:
        print(f"✅ Пост запланирован на {scheduled_time}")
    else:
        print("❌ Не удалось запланировать пост")

def example_response_generation():
    """Пример генерации ответов на сообщения"""
    print("💬 Пример: Генерация ответов")
    
    load_dotenv()
    config = Config()
    
    ai_generator = AIContentGenerator(config)
    
    # Симулируем разные типы сообщений
    test_messages = [
        ("Привет! Как дела?", "greeting"),
        ("Что думаешь о новом Python 3.12?", "question"),
        ("Можешь помочь с Docker?", "help"),
        ("Отличная статья про микросервисы!", "general")
    ]
    
    for message, msg_type in test_messages:
        print(f"\n📨 Исходное сообщение: {message}")
        
        response = ai_generator.generate_response(message, "test_user")
        
        if response:
            print(f"🤖 Ответ: {response}")
        else:
            print("❌ Не удалось сгенерировать ответ")

def example_analytics_usage():
    """Пример использования аналитики"""
    print("📊 Пример: Работа с аналитикой")
    
    load_dotenv()
    config = Config()
    
    analytics = Analytics(config)
    
    # Получаем аналитику за последние 7 дней
    post_analytics = analytics.get_post_analytics(7)
    
    print("Статистика постов за 7 дней:")
    print(f"• Всего постов: {post_analytics.get('total_posts', 0)}")
    print(f"• Средняя вовлеченность: {post_analytics.get('avg_engagement_rate', 0)}%")
    print(f"• Всего лайков: {post_analytics.get('total_likes', 0)}")
    
    # Получаем ежедневную статистику
    daily_stats = analytics.get_daily_stats(7)
    
    if daily_stats:
        print("\nЕжедневная активность:")
        for day in daily_stats[:3]:  # Показываем последние 3 дня
            print(f"• {day['date']}: {day['posts_published']} постов")

def example_content_themes():
    """Пример работы с разными темами контента"""
    print("🎨 Пример: Разные темы контента")
    
    load_dotenv()
    config = Config()
    
    ai_generator = AIContentGenerator(config)
    
    # Настраиваем разные темы
    themes = ["programming", "ai", "devops", "security", "cloud"]
    
    for theme in themes:
        post = ai_generator.generate_post(theme)
        
        if post:
            print(f"\n🎯 Тема: {theme}")
            print(f"📝 Пост: {post[:100]}...")
        
        # Небольшая пауза между генерацией
        import time
        time.sleep(1)

def example_message_analysis():
    """Пример анализа сообщений"""
    print("🔍 Пример: Анализ сообщений")
    
    load_dotenv()
    config = Config()
    
    ai_generator = AIContentGenerator(config)
    
    # Тестовые сообщения для анализа
    messages = [
        "Отличная работа! Продолжай в том же духе! 👍",
        "Это полная ерунда, не согласен с тобой",
        "Интересная точка зрения, но есть вопросы",
        "Спам спам спам купите сейчас!",
        "Как настроить Docker для продакшена?"
    ]
    
    for message in messages:
        sentiment = ai_generator.analyze_sentiment(message)
        print(f"📝 '{message}' -> {sentiment}")

def example_custom_configuration():
    """Пример настройки конфигурации"""
    print("⚙️ Пример: Настройка конфигурации")
    
    # Создаем конфигурацию с кастомными настройками
    config = Config()
    
    # Показываем текущие настройки
    print("Текущие настройки:")
    print(f"• Язык контента: {config.CONTENT_LANGUAGE}")
    print(f"• Максимум постов в день: {config.MAX_POSTS_PER_DAY}")
    print(f"• Время публикации: {config.POSTING_SCHEDULE_HOUR}:{config.POSTING_SCHEDULE_MINUTE:02d}")
    print(f"• Темы: {', '.join(config.POST_THEMES)}")
    print(f"• Количество хештегов: {config.HASHTAG_COUNT}")
    print(f"• Автоответы: {'включены' if config.RESPONSE_ENABLED else 'отключены'}")

def run_all_examples():
    """Запускает все примеры"""
    print("🚀 Запуск всех примеров AI Twitter Agent\n")
    
    examples = [
        ("Базовый пост", example_basic_post),
        ("Создание треда", example_thread_creation),
        ("Планирование постов", example_scheduled_posting),
        ("Генерация ответов", example_response_generation),
        ("Работа с аналитикой", example_analytics_usage),
        ("Разные темы контента", example_content_themes),
        ("Анализ сообщений", example_message_analysis),
        ("Настройка конфигурации", example_custom_configuration)
    ]
    
    for example_name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"📋 {example_name}")
        print('='*60)
        
        try:
            example_func()
            print("✅ Пример выполнен успешно")
        except Exception as e:
            print(f"❌ Ошибка в примере: {e}")
        
        print()

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        example_name = sys.argv[1].lower()
        
        examples_map = {
            "post": example_basic_post,
            "thread": example_thread_creation,
            "schedule": example_scheduled_posting,
            "response": example_response_generation,
            "analytics": example_analytics_usage,
            "themes": example_content_themes,
            "analysis": example_message_analysis,
            "config": example_custom_configuration
        }
        
        if example_name in examples_map:
            examples_map[example_name]()
        else:
            print(f"❌ Неизвестный пример: {example_name}")
            print("Доступные примеры:", ", ".join(examples_map.keys()))
    else:
        run_all_examples()

if __name__ == "__main__":
    main()
