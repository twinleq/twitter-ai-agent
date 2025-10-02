#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Twitter Agent - Главный файл для запуска бота
Автоматически ведет Twitter аккаунт, генерирует посты и отвечает на сообщения
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Импорт наших модулей
from src.config import Config
from src.twitter_client import TwitterClient
from src.ai_content_generator import AIContentGenerator
from src.post_scheduler import PostScheduler
from src.message_handler import MessageHandler
from src.analytics import Analytics
from src.utils import setup_logging

def main():
    """Основная функция запуска AI Twitter Agent"""
    
    # Загружаем конфигурацию
    load_dotenv()
    config = Config()
    
    # Настраиваем логирование
    setup_logging(config.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Запуск AI Twitter Agent...")
    logger.info(f"📊 Режим работы: {'Продакшн' if config.PRODUCTION_MODE else 'Тест'}")
    
    try:
        # Инициализируем компоненты
        twitter_client = TwitterClient(config)
        ai_generator = AIContentGenerator(config)
        scheduler = PostScheduler(config, twitter_client, ai_generator)
        message_handler = MessageHandler(config, twitter_client, ai_generator)
        analytics = Analytics(config)
        
        logger.info("✅ Все компоненты успешно инициализированы")
        
        # Проверяем подключение к Twitter API
        if twitter_client.verify_credentials():
            logger.info("✅ Подключение к Twitter API успешно")
        else:
            logger.error("❌ Ошибка подключения к Twitter API")
            return
        
        # Запускаем планировщик постов
        if config.AUTO_POSTING_ENABLED:
            scheduler.start()
            logger.info(f"📅 Планировщик постов запущен (пост в {config.POSTING_SCHEDULE_HOUR}:{config.POSTING_SCHEDULE_MINUTE:02d})")
        
        # Запускаем обработчик сообщений
        if config.RESPONSE_ENABLED:
            message_handler.start()
            logger.info("💬 Обработчик сообщений запущен")
        
        # Основной цикл работы
        logger.info("🔄 AI Twitter Agent работает...")
        while True:
            try:
                # Проверяем новые сообщения
                if config.RESPONSE_ENABLED:
                    message_handler.process_messages()
                
                # Обновляем аналитику
                if config.ENABLE_ANALYTICS:
                    analytics.update_metrics()
                
                # Ждем перед следующей итерацией
                time.sleep(config.CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("🛑 Получен сигнал остановки...")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(60)  # Ждем минуту перед повторной попыткой
        
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
    
    finally:
        logger.info("👋 AI Twitter Agent остановлен")

if __name__ == "__main__":
    main()
