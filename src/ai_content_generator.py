#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Generator для Twitter Agent
Генерирует посты, ответы и контент с помощью OpenAI
"""

import openai
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .config import Config
from .utils import clean_text, generate_hashtags, validate_tweet_length, truncate_tweet

class AIContentGenerator:
    """Генератор контента на основе AI"""
    
    def __init__(self, config: Config):
        """Инициализация генератора контента"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Настройка OpenAI
        openai.api_key = config.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 150
        self.temperature = 0.7
        
        # Шаблоны для генерации контента
        self.post_templates = self._load_post_templates()
        self.response_templates = self._load_response_templates()
        
        self.logger.info("✅ AI Content Generator инициализирован")
    
    def _load_post_templates(self) -> List[str]:
        """Загружает шаблоны для постов"""
        if self.config.CONTENT_LANGUAGE == 'ru':
            return [
                "Напиши интересный пост о {topic} для разработчиков. Включи практический совет.",
                "Создай мотивирующий пост про {topic} с личным опытом.",
                "Напиши образовательный твит о {topic} с полезным советом.",
                "Создай пост про {topic} который заинтересует IT-сообщество.",
                "Напиши вдохновляющий пост о {topic} для программистов."
            ]
        else:
            return [
                "Write an interesting post about {topic} for developers. Include a practical tip.",
                "Create a motivational post about {topic} with personal experience.",
                "Write an educational tweet about {topic} with a useful tip.",
                "Create a post about {topic} that will interest the IT community.",
                "Write an inspiring post about {topic} for programmers."
            ]
    
    def _load_response_templates(self) -> List[str]:
        """Загружает шаблоны для ответов"""
        if self.config.CONTENT_LANGUAGE == 'ru':
            return [
                "Спасибо за интересный вопрос! {response}",
                "Отличная мысль! {response}",
                "Согласен с вами. {response}",
                "Интересная точка зрения! {response}",
                "Хороший вопрос! {response}"
            ]
        else:
            return [
                "Thanks for the interesting question! {response}",
                "Great thought! {response}",
                "I agree with you. {response}",
                "Interesting point of view! {response}",
                "Good question! {response}"
            ]
    
    def generate_post(self, topic: Optional[str] = None, context: Optional[Dict] = None) -> Optional[str]:
        """Генерирует новый пост"""
        try:
            # Выбираем случайную тему если не указана
            if not topic:
                topic = random.choice(self.config.POST_THEMES)
            
            # Выбираем случайный шаблон
            template = random.choice(self.post_templates)
            prompt = template.format(topic=topic)
            
            # Добавляем контекст если есть
            if context:
                prompt += f"\n\nКонтекст: {context.get('context', '')}"
            
            # Добавляем ограничения
            prompt += f"\n\nОграничения: Максимум {self.config.MAX_TWEET_LENGTH} символов, на русском языке, без эмодзи в начале."
            
            # Генерируем контент
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Ты эксперт в области {topic} и пишешь интересные посты для Twitter. Твой стиль: профессиональный, но дружелюбный, с практическими советами."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            content = clean_text(content)
            
            # Добавляем хештеги
            hashtags = generate_hashtags([topic], self.config.HASHTAG_COUNT, self.config.CONTENT_LANGUAGE)
            hashtag_text = " ".join(hashtags)
            
            # Объединяем контент с хештегами
            full_post = f"{content}\n\n{hashtag_text}"
            
            # Проверяем длину и обрезаем если нужно
            if not validate_tweet_length(full_post, self.config.MAX_TWEET_LENGTH):
                # Сначала пробуем сократить хештеги
                if len(hashtags) > 1:
                    hashtags = hashtags[:len(hashtags)-1]
                    hashtag_text = " ".join(hashtags)
                    full_post = f"{content}\n\n{hashtag_text}"
                
                # Если все еще не помещается, обрезаем контент
                if not validate_tweet_length(full_post, self.config.MAX_TWEET_LENGTH):
                    available_length = self.config.MAX_TWEET_LENGTH - len(hashtag_text) - 3  # -3 для \n\n
                    content = truncate_tweet(content, available_length)
                    full_post = f"{content}\n\n{hashtag_text}"
            
            self.logger.info(f"✅ Сгенерирован пост на тему '{topic}'")
            return full_post
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации поста: {e}")
            return None
    
    def generate_response(self, original_tweet: str, mention_user: str, context: Optional[Dict] = None) -> Optional[str]:
        """Генерирует ответ на твит"""
        try:
            # Выбираем случайный шаблон ответа
            template = random.choice(self.response_templates)
            
            prompt = f"Ответь на этот твит от @{mention_user}: '{original_tweet}'\n\n"
            prompt += f"Используй шаблон: {template}\n\n"
            prompt += f"Ограничения: Максимум {self.config.MAX_TWEET_LENGTH} символов, на русском языке, вежливо и конструктивно."
            
            if context:
                prompt += f"\n\nДополнительный контекст: {context.get('context', '')}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты вежливый и конструктивный пользователь Twitter. Отвечаешь на твиты профессионально, но дружелюбно."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.5  # Более низкая температура для ответов
            )
            
            content = response.choices[0].message.content.strip()
            content = clean_text(content)
            
            # Обрезаем если нужно
            if not validate_tweet_length(content, self.config.MAX_TWEET_LENGTH):
                content = truncate_tweet(content, self.config.MAX_TWEET_LENGTH)
            
            self.logger.info(f"✅ Сгенерирован ответ для @{mention_user}")
            return content
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации ответа: {e}")
            return None
    
    def generate_thread(self, main_topic: str, thread_length: int = 3) -> Optional[List[str]]:
        """Генерирует тред (несколько связанных твитов)"""
        try:
            prompt = f"Создай тред из {thread_length} твитов на тему '{main_topic}'.\n\n"
            prompt += "Каждый твит должен быть пронумерован (1/3, 2/3, и т.д.) и логически связан с предыдущим.\n"
            prompt += f"Максимум {self.config.MAX_TWEET_LENGTH} символов на твит, на русском языке."
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты создаешь качественные треды для Twitter. Каждый твит в треде должен быть ценным и связанным с общей темой."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens * thread_length,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Разделяем на отдельные твиты
            tweets = []
            lines = content.split('\n')
            current_tweet = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Проверяем, начинается ли новая нумерация (новый твит)
                if re.match(r'^\d+/\d+', line):
                    if current_tweet:
                        tweets.append(clean_text(current_tweet))
                    current_tweet = line
                else:
                    current_tweet += " " + line if current_tweet else line
            
            # Добавляем последний твит
            if current_tweet:
                tweets.append(clean_text(current_tweet))
            
            # Добавляем хештеги к последнему твиту
            if tweets:
                hashtags = generate_hashtags([main_topic], self.config.HASHTAG_COUNT, self.config.CONTENT_LANGUAGE)
                hashtag_text = " ".join(hashtags)
                
                last_tweet = tweets[-1]
                if validate_tweet_length(f"{last_tweet}\n\n{hashtag_text}", self.config.MAX_TWEET_LENGTH):
                    tweets[-1] = f"{last_tweet}\n\n{hashtag_text}"
            
            self.logger.info(f"✅ Сгенерирован тред из {len(tweets)} твитов")
            return tweets
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации треда: {e}")
            return None
    
    def generate_topic_suggestion(self) -> str:
        """Генерирует предложение темы для поста"""
        return random.choice(self.config.POST_THEMES)
    
    def analyze_sentiment(self, text: str) -> str:
        """Анализирует тональность текста"""
        try:
            prompt = f"Проанализируй тональность этого текста: '{text}'\n\n"
            prompt += "Ответь одним словом: позитивный, негативный, или нейтральный."
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты анализируешь тональность текстов. Отвечай кратко и точно."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            return sentiment
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка анализа тональности: {e}")
            return "нейтральный"
    
    def get_content_ideas(self, count: int = 5) -> List[str]:
        """Получает идеи для контента"""
        ideas = []
        for _ in range(count):
            topic = self.generate_topic_suggestion()
            ideas.append(f"Пост про {topic}")
        
        return ideas
