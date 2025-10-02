#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Message Handler для AI Twitter Agent
Обрабатывает упоминания, прямые сообщения и автоматически отвечает
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import json
import os
import re
from .config import Config
from .twitter_client import TwitterClient
from .ai_content_generator import AIContentGenerator
from .utils import (
    extract_mentions, extract_hashtags, safe_json_loads, safe_json_dumps, 
    format_timestamp, get_random_delay, clean_text
)

class MessageHandler:
    """Обработчик сообщений и упоминаний"""
    
    def __init__(self, config: Config, twitter_client: TwitterClient, ai_generator: AIContentGenerator):
        """Инициализация обработчика сообщений"""
        self.config = config
        self.twitter_client = twitter_client
        self.ai_generator = ai_generator
        self.logger = logging.getLogger(__name__)
        
        # Файлы для хранения данных
        self.mentions_file = './data/processed_mentions.json'
        self.dm_file = './data/processed_dms.json'
        self.response_history_file = './data/response_history.json'
        
        # Создаем директорию для данных
        os.makedirs('./data', exist_ok=True)
        
        # Загружаем обработанные сообщения
        self.processed_mentions = self._load_processed_mentions()
        self.processed_dms = self._load_processed_dms()
        self.response_history = self._load_response_history()
        
        # Ключевые слова для определения типа сообщения
        self.greeting_keywords = ['привет', 'hello', 'hi', 'добро', 'утро', 'день', 'вечер']
        self.question_keywords = ['как', 'что', 'где', 'когда', 'почему', 'зачем', '?', 'how', 'what', 'where', 'when', 'why']
        self.help_keywords = ['помощь', 'help', 'поддержка', 'support']
        
        self.logger.info("✅ Message Handler инициализирован")
    
    def _load_processed_mentions(self) -> Set[str]:
        """Загружает список обработанных упоминаний"""
        try:
            if os.path.exists(self.mentions_file):
                with open(self.mentions_file, 'r', encoding='utf-8') as f:
                    data = safe_json_loads(f.read(), [])
                    return set(data)
            return set()
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки обработанных упоминаний: {e}")
            return set()
    
    def _save_processed_mentions(self):
        """Сохраняет список обработанных упоминаний"""
        try:
            with open(self.mentions_file, 'w', encoding='utf-8') as f:
                f.write(safe_json_dumps(list(self.processed_mentions)))
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения обработанных упоминаний: {e}")
    
    def _load_processed_dms(self) -> Set[str]:
        """Загружает список обработанных DM"""
        try:
            if os.path.exists(self.dm_file):
                with open(self.dm_file, 'r', encoding='utf-8') as f:
                    data = safe_json_loads(f.read(), [])
                    return set(data)
            return set()
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки обработанных DM: {e}")
            return set()
    
    def _save_processed_dms(self):
        """Сохраняет список обработанных DM"""
        try:
            with open(self.dm_file, 'w', encoding='utf-8') as f:
                f.write(safe_json_dumps(list(self.processed_dms)))
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения обработанных DM: {e}")
    
    def _load_response_history(self) -> List[Dict]:
        """Загружает историю ответов"""
        try:
            if os.path.exists(self.response_history_file):
                with open(self.response_history_file, 'r', encoding='utf-8') as f:
                    data = safe_json_loads(f.read(), [])
                    return data if isinstance(data, list) else []
            return []
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки истории ответов: {e}")
            return []
    
    def _save_response_history(self):
        """Сохраняет историю ответов"""
        try:
            with open(self.response_history_file, 'w', encoding='utf-8') as f:
                f.write(safe_json_dumps(self.response_history))
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения истории ответов: {e}")
    
    def _analyze_message_type(self, text: str) -> str:
        """Анализирует тип сообщения"""
        text_lower = text.lower()
        
        # Проверяем на приветствие
        if any(keyword in text_lower for keyword in self.greeting_keywords):
            return 'greeting'
        
        # Проверяем на вопрос
        if any(keyword in text_lower for keyword in self.question_keywords):
            return 'question'
        
        # Проверяем на просьбу о помощи
        if any(keyword in text_lower for keyword in self.help_keywords):
            return 'help'
        
        # Проверяем на спам или нежелательный контент
        if self._is_spam(text):
            return 'spam'
        
        return 'general'
    
    def _is_spam(self, text: str) -> bool:
        """Проверяет, является ли сообщение спамом"""
        spam_indicators = [
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',  # URL
            r'follow\s+me',  # follow me
            r'check\s+out',  # check out
            r'buy\s+now',    # buy now
            r'discount',     # discount
            r'free\s+money', # free money
        ]
        
        text_lower = text.lower()
        for pattern in spam_indicators:
            if re.search(pattern, text_lower):
                return True
        
        # Проверяем на черный список слов
        if any(word in text_lower for word in self.config.BLACKLISTED_WORDS):
            return True
        
        return False
    
    def _should_respond(self, message_type: str, user_id: str) -> bool:
        """Определяет, нужно ли отвечать на сообщение"""
        # Не отвечаем на спам
        if message_type == 'spam':
            return False
        
        # Проверяем, не отвечали ли мы уже этому пользователю недавно
        recent_responses = [
            resp for resp in self.response_history 
            if resp.get('user_id') == user_id and 
            datetime.strptime(resp.get('timestamp', ''), '%Y-%m-%d %H:%M:%S') > 
            datetime.now() - timedelta(hours=1)
        ]
        
        # Не более 3 ответов в час одному пользователю
        if len(recent_responses) >= 3:
            return False
        
        return True
    
    def _generate_contextual_response(self, message: Dict, message_type: str) -> Optional[str]:
        """Генерирует контекстуальный ответ"""
        try:
            text = message['text']
            user_id = message['author_id']
            
            # Создаем контекст для AI
            context = {
                'message_type': message_type,
                'original_text': text,
                'user_id': user_id,
                'language': self.config.CONTENT_LANGUAGE
            }
            
            # Генерируем ответ в зависимости от типа сообщения
            if message_type == 'greeting':
                response = self.ai_generator.generate_response(
                    text, user_id, 
                    {'context': 'Это приветствие, ответь дружелюбно и кратко'}
                )
            elif message_type == 'question':
                response = self.ai_generator.generate_response(
                    text, user_id,
                    {'context': 'Это вопрос, дай полезный и конструктивный ответ'}
                )
            elif message_type == 'help':
                response = self.ai_generator.generate_response(
                    text, user_id,
                    {'context': 'Пользователь просит помощи, предложи варианты поддержки'}
                )
            else:
                response = self.ai_generator.generate_response(
                    text, user_id,
                    {'context': 'Отвечай вежливо и конструктивно на общее сообщение'}
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации ответа: {e}")
            return None
    
    def process_mentions(self):
        """Обрабатывает новые упоминания"""
        try:
            if not self.config.RESPONSE_ENABLED:
                return
            
            # Получаем новые упоминания
            mentions = self.twitter_client.get_mentions(count=20)
            
            for mention in mentions:
                mention_id = mention['id']
                
                # Пропускаем уже обработанные
                if mention_id in self.processed_mentions:
                    continue
                
                # Анализируем тип сообщения
                message_type = self._analyze_message_type(mention['text'])
                
                # Проверяем, нужно ли отвечать
                if not self._should_respond(message_type, mention['author_id']):
                    self.processed_mentions.add(mention_id)
                    self._save_processed_mentions()
                    continue
                
                # Генерируем ответ
                response = self._generate_contextual_response(mention, message_type)
                
                if response:
                    # Добавляем случайную задержку
                    delay = get_random_delay(
                        self.config.RESPONSE_DELAY_MIN,
                        self.config.RESPONSE_DELAY_MAX
                    )
                    time.sleep(delay)
                    
                    # Отправляем ответ
                    reply_id = self.twitter_client.reply_to_tweet(mention_id, response)
                    
                    if reply_id:
                        # Сохраняем в историю
                        self._add_to_response_history({
                            'type': 'mention_reply',
                            'original_tweet_id': mention_id,
                            'reply_id': reply_id,
                            'user_id': mention['author_id'],
                            'message_type': message_type,
                            'response': response,
                            'timestamp': format_timestamp(datetime.now())
                        })
                        
                        self.logger.info(f"✅ Ответ на упоминание отправлен: {reply_id}")
                    else:
                        self.logger.error(f"❌ Не удалось отправить ответ на упоминание: {mention_id}")
                
                # Отмечаем как обработанное
                self.processed_mentions.add(mention_id)
                self._save_processed_mentions()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки упоминаний: {e}")
    
    def process_direct_messages(self):
        """Обрабатывает прямые сообщения"""
        try:
            if not self.config.RESPONSE_ENABLED:
                return
            
            # Получаем новые DM
            dms = self.twitter_client.get_direct_messages(count=20)
            
            for dm in dms:
                dm_id = dm['id']
                
                # Пропускаем уже обработанные
                if dm_id in self.processed_dms:
                    continue
                
                # Анализируем тип сообщения
                message_type = self._analyze_message_type(dm['text'])
                
                # Проверяем, нужно ли отвечать
                if not self._should_respond(message_type, dm['sender_id']):
                    self.processed_dms.add(dm_id)
                    self._save_processed_dms()
                    continue
                
                # Генерируем ответ
                response = self._generate_contextual_response(dm, message_type)
                
                if response:
                    # Отправляем DM
                    success = self.twitter_client.send_direct_message(dm['sender_id'], response)
                    
                    if success:
                        # Сохраняем в историю
                        self._add_to_response_history({
                            'type': 'dm_reply',
                            'original_dm_id': dm_id,
                            'user_id': dm['sender_id'],
                            'message_type': message_type,
                            'response': response,
                            'timestamp': format_timestamp(datetime.now())
                        })
                        
                        self.logger.info(f"✅ Ответ в DM отправлен пользователю {dm['sender_id']}")
                    else:
                        self.logger.error(f"❌ Не удалось отправить DM ответ")
                
                # Отмечаем как обработанное
                self.processed_dms.add(dm_id)
                self._save_processed_dms()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки DM: {e}")
    
    def process_messages(self):
        """Основная функция обработки сообщений"""
        try:
            self.process_mentions()
            self.process_direct_messages()
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки сообщений: {e}")
    
    def _add_to_response_history(self, response_data: Dict):
        """Добавляет ответ в историю"""
        self.response_history.append(response_data)
        
        # Ограничиваем историю последними 1000 ответов
        if len(self.response_history) > 1000:
            self.response_history = self.response_history[-1000:]
        
        self._save_response_history()
    
    def start(self):
        """Запускает обработчик сообщений в отдельном потоке"""
        import threading
        
        def run_handler():
            while True:
                try:
                    self.process_messages()
                    time.sleep(self.config.MESSAGE_CHECK_INTERVAL)
                except Exception as e:
                    self.logger.error(f"❌ Ошибка в обработчике сообщений: {e}")
                    time.sleep(60)
        
        handler_thread = threading.Thread(target=run_handler, daemon=True)
        handler_thread.start()
        self.logger.info("🚀 Message Handler запущен")
    
    def get_response_statistics(self) -> Dict:
        """Возвращает статистику ответов"""
        total_responses = len(self.response_history)
        
        # Статистика по типам сообщений
        message_types = {}
        for response in self.response_history:
            msg_type = response.get('message_type', 'unknown')
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Статистика по типам ответов
        response_types = {}
        for response in self.response_history:
            resp_type = response.get('type', 'unknown')
            response_types[resp_type] = response_types.get(resp_type, 0) + 1
        
        # Ответы за последние 24 часа
        recent_responses = 0
        cutoff_time = datetime.now() - timedelta(hours=24)
        for response in self.response_history:
            try:
                resp_time = datetime.strptime(response.get('timestamp', ''), '%Y-%m-%d %H:%M:%S')
                if resp_time >= cutoff_time:
                    recent_responses += 1
            except:
                continue
        
        return {
            'total_responses': total_responses,
            'recent_responses_24h': recent_responses,
            'message_types': message_types,
            'response_types': response_types,
            'processed_mentions': len(self.processed_mentions),
            'processed_dms': len(self.processed_dms)
        }
    
    def manual_response(self, tweet_id: str, response_text: str) -> bool:
        """Ручной ответ на твит"""
        try:
            reply_id = self.twitter_client.reply_to_tweet(tweet_id, response_text)
            
            if reply_id:
                # Сохраняем в историю
                self._add_to_response_history({
                    'type': 'manual_reply',
                    'original_tweet_id': tweet_id,
                    'reply_id': reply_id,
                    'response': response_text,
                    'timestamp': format_timestamp(datetime.now())
                })
                
                self.logger.info(f"✅ Ручной ответ отправлен: {reply_id}")
                return True
            else:
                self.logger.error(f"❌ Не удалось отправить ручной ответ")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка ручного ответа: {e}")
            return False
