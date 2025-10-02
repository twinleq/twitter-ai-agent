#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты для AI Twitter Agent
Вспомогательные функции для работы бота
"""

import logging
import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import string

def setup_logging(log_level: str = 'INFO', log_file: str = './logs/twitter_agent.log'):
    """Настраивает систему логирования"""
    
    # Создаем директорию для логов если её нет
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Настраиваем формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настраиваем уровень логирования
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Конфигурация логирования
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def clean_text(text: str) -> str:
    """Очищает текст от лишних символов и форматирует"""
    if not text:
        return ""
    
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Убираем специальные символы в начале и конце
    text = text.strip('.,!?;:"()[]{}')
    
    return text

def generate_hashtags(topics: List[str], count: int = 3, language: str = 'ru') -> List[str]:
    """Генерирует хештеги на основе тем"""
    if language == 'ru':
        hashtag_map = {
            'technology': '#технологии',
            'programming': '#программирование', 
            'ai': '#ии',
            'devops': '#devops',
            'automation': '#автоматизация',
            'coding': '#кодинг',
            'development': '#разработка',
            'software': '#софт',
            'cloud': '#облако',
            'security': '#безопасность',
            'data': '#данные',
            'machine_learning': '#машинноеобучение'
        }
    else:
        hashtag_map = {
            'technology': '#technology',
            'programming': '#programming',
            'ai': '#AI',
            'devops': '#devops', 
            'automation': '#automation',
            'coding': '#coding',
            'development': '#development',
            'software': '#software',
            'cloud': '#cloud',
            'security': '#security',
            'data': '#data',
            'machine_learning': '#MachineLearning'
        }
    
    # Выбираем случайные хештеги из доступных тем
    available_hashtags = [hashtag_map.get(topic.lower(), f'#{topic}') for topic in topics]
    return random.sample(available_hashtags, min(count, len(available_hashtags)))

def validate_tweet_length(text: str, max_length: int = 280) -> bool:
    """Проверяет длину твита"""
    return len(text) <= max_length

def truncate_tweet(text: str, max_length: int = 280, suffix: str = '...') -> str:
    """Обрезает твит до нужной длины"""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    # Обрезаем по последнему пробелу чтобы не разрывать слова
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + suffix

def extract_mentions(text: str) -> List[str]:
    """Извлекает упоминания из текста"""
    mention_pattern = r'@(\w+)'
    return re.findall(mention_pattern, text)

def extract_hashtags(text: str) -> List[str]:
    """Извлекает хештеги из текста"""
    hashtag_pattern = r'#(\w+)'
    return re.findall(hashtag_pattern, text)

def calculate_engagement_score(likes: int, retweets: int, replies: int, followers: int) -> float:
    """Вычисляет показатель вовлеченности"""
    if followers == 0:
        return 0.0
    
    engagement = (likes + retweets * 2 + replies * 3) / followers * 100
    return round(engagement, 2)

def generate_random_id(length: int = 8) -> str:
    """Генерирует случайный ID"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Безопасная загрузка JSON"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = '{}') -> str:
    """Безопасное сохранение в JSON"""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default

def hash_text(text: str) -> str:
    """Создает хеш текста для уникальной идентификации"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def format_timestamp(timestamp: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Форматирует временную метку"""
    return timestamp.strftime(format_str)

def parse_timestamp(timestamp_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """Парсит временную метку из строки"""
    try:
        return datetime.strptime(timestamp_str, format_str)
    except ValueError:
        return None

def is_business_hours(dt: datetime = None) -> bool:
    """Проверяет, рабочее ли время (9:00 - 18:00)"""
    if dt is None:
        dt = datetime.now()
    
    # Проверяем день недели (0 = понедельник, 6 = воскресенье)
    if dt.weekday() >= 5:  # Выходные
        return False
    
    # Проверяем время
    hour = dt.hour
    return 9 <= hour <= 18

def get_random_delay(min_seconds: int = 5, max_seconds: int = 30) -> int:
    """Возвращает случайную задержку в секундах"""
    return random.randint(min_seconds, max_seconds)

def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    # Убираем недопустимые символы
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Убираем лишние пробелы
    filename = filename.strip()
    # Ограничиваем длину
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def create_backup_filename(base_name: str, extension: str = '.json') -> str:
    """Создает имя файла для резервной копии"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_backup_{timestamp}{extension}"
