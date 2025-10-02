#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для AI Twitter Agent
Позволяет быстро протестировать функционал без полного запуска
"""

import os
import sys
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.twitter_client import TwitterClient
from src.ai_content_generator import AIContentGenerator
from src.utils import setup_logging

def test_configuration():
    """Тестирует конфигурацию"""
    print("🔧 Тестирование конфигурации...")
    
    load_dotenv()
    config = Config()
    
    if config.validate():
        print("✅ Конфигурация корректна")
        return True
    else:
        print("❌ Конфигурация содержит ошибки")
        return False

def test_twitter_api():
    """Тестирует подключение к Twitter API"""
    print("🐦 Тестирование Twitter API...")
    
    try:
        load_dotenv()
        config = Config()
        twitter_client = TwitterClient(config)
        
        if twitter_client.verify_credentials():
            print("✅ Подключение к Twitter API успешно")
            
            # Получаем информацию о пользователе
            user_info = twitter_client.get_user_info(config.BOT_USERNAME)
            if user_info:
                print(f"👤 Пользователь: @{user_info['username']}")
                print(f"📊 Подписчики: {user_info['metrics']['followers_count']}")
                print(f"📝 Твиты: {user_info['metrics']['tweet_count']}")
            
            return True
        else:
            print("❌ Ошибка подключения к Twitter API")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка Twitter API: {e}")
        return False

def test_openai_api():
    """Тестирует подключение к OpenAI API"""
    print("🤖 Тестирование OpenAI API...")
    
    try:
        load_dotenv()
        config = Config()
        ai_generator = AIContentGenerator(config)
        
        # Генерируем тестовый пост
        test_post = ai_generator.generate_post("programming")
        
        if test_post:
            print("✅ Подключение к OpenAI API успешно")
            print(f"📝 Тестовый пост:\n{test_post}")
            return True
        else:
            print("❌ Не удалось сгенерировать пост")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка OpenAI API: {e}")
        return False

def test_content_generation():
    """Тестирует генерацию контента"""
    print("📝 Тестирование генерации контента...")
    
    try:
        load_dotenv()
        config = Config()
        ai_generator = AIContentGenerator(config)
        
        # Тестируем разные типы контента
        topics = ["programming", "ai", "devops"]
        
        for topic in topics:
            post = ai_generator.generate_post(topic)
            if post:
                print(f"✅ Пост на тему '{topic}' сгенерирован")
                print(f"   Длина: {len(post)} символов")
            else:
                print(f"❌ Не удалось сгенерировать пост на тему '{topic}'")
        
        # Тестируем генерацию треда
        thread = ai_generator.generate_thread("programming", 3)
        if thread:
            print(f"✅ Тред из {len(thread)} твитов сгенерирован")
            for i, tweet in enumerate(thread, 1):
                print(f"   {i}: {tweet[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации контента: {e}")
        return False

def test_message_analysis():
    """Тестирует анализ сообщений"""
    print("💬 Тестирование анализа сообщений...")
    
    try:
        load_dotenv()
        config = Config()
        ai_generator = AIContentGenerator(config)
        
        # Тестовые сообщения
        test_messages = [
            "Привет! Как дела?",
            "Что думаешь о новом Python 3.12?",
            "Можешь помочь с Docker?",
            "Check out this amazing discount!",
            "Спасибо за интересную информацию!"
        ]
        
        for message in test_messages:
            sentiment = ai_generator.analyze_sentiment(message)
            print(f"📝 '{message}' -> {sentiment}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа сообщений: {e}")
        return False

def test_dry_run_post():
    """Тестирует создание поста без публикации"""
    print("📝 Тестирование создания поста (без публикации)...")
    
    try:
        load_dotenv()
        config = Config()
        ai_generator = AIContentGenerator(config)
        
        # Генерируем пост
        post = ai_generator.generate_post("ai")
        
        if post:
            print("✅ Пост сгенерирован успешно:")
            print(f"\n{post}\n")
            print(f"📊 Статистика:")
            print(f"• Длина: {len(post)} символов")
            print(f"• Лимит: {config.MAX_TWEET_LENGTH} символов")
            print(f"• Помещается: {'✅' if len(post) <= config.MAX_TWEET_LENGTH else '❌'}")
            
            # Анализируем хештеги
            hashtags = [word for word in post.split() if word.startswith('#')]
            print(f"• Хештеги: {len(hashtags)} ({', '.join(hashtags)})")
            
            return True
        else:
            print("❌ Не удалось сгенерировать пост")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка создания поста: {e}")
        return False

def run_all_tests():
    """Запускает все тесты"""
    print("🧪 Запуск всех тестов AI Twitter Agent\n")
    
    setup_logging('INFO')
    
    tests = [
        ("Конфигурация", test_configuration),
        ("Twitter API", test_twitter_api),
        ("OpenAI API", test_openai_api),
        ("Генерация контента", test_content_generation),
        ("Анализ сообщений", test_message_analysis),
        ("Создание поста", test_dry_run_post)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Выводим итоги
    print(f"\n{'='*50}")
    print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"• {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Бот готов к работе.")
    else:
        print("⚠️ Некоторые тесты провалены. Проверьте конфигурацию.")
    
    return passed == total

def main():
    """Главная функция тестирования"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "config":
            test_configuration()
        elif test_name == "twitter":
            test_twitter_api()
        elif test_name == "openai":
            test_openai_api()
        elif test_name == "content":
            test_content_generation()
        elif test_name == "analysis":
            test_message_analysis()
        elif test_name == "post":
            test_dry_run_post()
        else:
            print(f"❌ Неизвестный тест: {test_name}")
            print("Доступные тесты: config, twitter, openai, content, analysis, post")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()
