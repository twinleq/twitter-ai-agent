#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация AI Twitter Agent
Управляет всеми настройками бота
"""

import os
from typing import List, Dict, Any

class Config:
    """Класс конфигурации для AI Twitter Agent"""
    
    def __init__(self):
        """Инициализация конфигурации из переменных окружения"""
        
        # Twitter API настройки
        self.TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
        self.TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
        self.TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
        self.TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
        self.TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
        
        # OpenAI API
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        
        # Основные настройки бота
        self.BOT_USERNAME = os.getenv('BOT_USERNAME', '')
        self.PRODUCTION_MODE = os.getenv('PRODUCTION_MODE', 'false').lower() == 'true'
        
        # Настройки постинга
        self.AUTO_POSTING_ENABLED = os.getenv('AUTO_POSTING_ENABLED', 'true').lower() == 'true'
        self.POSTING_SCHEDULE_HOUR = int(os.getenv('POSTING_SCHEDULE_HOUR', '9'))
        self.POSTING_SCHEDULE_MINUTE = int(os.getenv('POSTING_SCHEDULE_MINUTE', '0'))
        self.MAX_POSTS_PER_DAY = int(os.getenv('MAX_POSTS_PER_DAY', '5'))
        
        # Настройки ответов
        self.RESPONSE_ENABLED = os.getenv('RESPONSE_ENABLED', 'true').lower() == 'true'
        self.AUTO_RESPONSE_ENABLED = os.getenv('AUTO_RESPONSE_ENABLED', 'false').lower() == 'true'
        self.RESPONSE_DELAY_MIN = int(os.getenv('RESPONSE_DELAY_MIN', '5'))
        self.RESPONSE_DELAY_MAX = int(os.getenv('RESPONSE_DELAY_MAX', '30'))
        
        # Настройки контента
        self.CONTENT_LANGUAGE = os.getenv('CONTENT_LANGUAGE', 'ru')
        self.POST_THEMES = os.getenv('POST_THEMES', 'technology,programming,ai,devops,automation').split(',')
        self.HASHTAG_COUNT = int(os.getenv('HASHTAG_COUNT', '3'))
        self.MENTION_FOLLOWERS = os.getenv('MENTION_FOLLOWERS', 'false').lower() == 'true'
        self.MAX_TWEET_LENGTH = int(os.getenv('MAX_TWEET_LENGTH', '280'))
        
        # Аналитика
        self.ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
        self.ANALYTICS_DB_PATH = os.getenv('ANALYTICS_DB_PATH', './data/analytics.db')
        
        # Логирование
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', './logs/twitter_agent.log')
        
        # Интервалы проверки
        self.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 минут
        self.MESSAGE_CHECK_INTERVAL = int(os.getenv('MESSAGE_CHECK_INTERVAL', '60'))  # 1 минута
        
        # Безопасность
        self.BLACKLISTED_WORDS = os.getenv('BLACKLISTED_WORDS', '').split(',') if os.getenv('BLACKLISTED_WORDS') else []
        self.MAX_FOLLOWERS_TO_MENTION = int(os.getenv('MAX_FOLLOWERS_TO_MENTION', '10'))
        
        # Резервное копирование
        self.BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        self.BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
        
    def validate(self) -> bool:
        """Проверяет корректность конфигурации"""
        required_fields = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET', 
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET',
            'OPENAI_API_KEY'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Отсутствуют обязательные поля конфигурации: {', '.join(missing_fields)}")
            return False
        
        if self.POSTING_SCHEDULE_HOUR < 0 or self.POSTING_SCHEDULE_HOUR > 23:
            print("❌ Некорректное время постинга (должно быть от 0 до 23)")
            return False
            
        if self.POSTING_SCHEDULE_MINUTE < 0 or self.POSTING_SCHEDULE_MINUTE > 59:
            print("❌ Некорректные минуты постинга (должно быть от 0 до 59)")
            return False
        
        return True
    
    def get_twitter_credentials(self) -> Dict[str, str]:
        """Возвращает учетные данные Twitter"""
        return {
            'api_key': self.TWITTER_API_KEY,
            'api_secret': self.TWITTER_API_SECRET,
            'access_token': self.TWITTER_ACCESS_TOKEN,
            'access_token_secret': self.TWITTER_ACCESS_TOKEN_SECRET,
            'bearer_token': self.TWITTER_BEARER_TOKEN
        }
    
    def get_openai_config(self) -> Dict[str, str]:
        """Возвращает конфигурацию OpenAI"""
        return {
            'api_key': self.OPENAI_API_KEY,
            'model': 'gpt-3.5-turbo',
            'max_tokens': 150,
            'temperature': 0.7
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию в виде словаря"""
        return {
            key: value for key, value in self.__dict__.items() 
            if not key.startswith('_') and 'SECRET' not in key and 'KEY' not in key
        }
