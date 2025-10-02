#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Client для AI Twitter Agent
Обеспечивает взаимодействие с Twitter API
"""

import tweepy
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from .config import Config
from .utils import calculate_engagement_score, format_timestamp

class TwitterClient:
    """Клиент для работы с Twitter API"""
    
    def __init__(self, config: Config):
        """Инициализация Twitter клиента"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Настройка API
        credentials = config.get_twitter_credentials()
        
        try:
            # Инициализация API v2
            self.client = tweepy.Client(
                bearer_token=credentials['bearer_token'],
                consumer_key=credentials['api_key'],
                consumer_secret=credentials['api_secret'],
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # Инициализация API v1.1 для некоторых функций
            auth = tweepy.OAuth1UserHandler(
                credentials['api_key'],
                credentials['api_secret'],
                credentials['access_token'],
                credentials['access_token_secret']
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            self.logger.info("✅ Twitter клиент инициализирован")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Twitter клиента: {e}")
            raise
    
    def verify_credentials(self) -> bool:
        """Проверяет подключение к Twitter API"""
        try:
            user = self.client.get_me()
            if user.data:
                self.logger.info(f"✅ Подключение к Twitter успешно. Пользователь: @{user.data.username}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка проверки учетных данных: {e}")
            return False
    
    def post_tweet(self, text: str, reply_to: Optional[str] = None) -> Optional[str]:
        """Публикует твит"""
        try:
            if reply_to:
                response = self.client.create_tweet(text=text, in_reply_to_tweet_id=reply_to)
            else:
                response = self.client.create_tweet(text=text)
            
            if response.data:
                tweet_id = response.data['id']
                self.logger.info(f"✅ Твит опубликован: {tweet_id}")
                return tweet_id
            else:
                self.logger.error("❌ Не удалось получить ID твита")
                return None
                
        except tweepy.TooManyRequests:
            self.logger.warning("⚠️ Превышен лимит запросов Twitter API")
            return None
        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации твита: {e}")
            return None
    
    def post_thread(self, tweets: List[str]) -> List[str]:
        """Публикует тред (несколько связанных твитов)"""
        tweet_ids = []
        reply_to_id = None
        
        try:
            for i, tweet_text in enumerate(tweets):
                tweet_id = self.post_tweet(tweet_text, reply_to=reply_to_id)
                if tweet_id:
                    tweet_ids.append(tweet_id)
                    reply_to_id = tweet_id
                    
                    # Небольшая задержка между твитами в треде
                    if i < len(tweets) - 1:
                        import time
                        time.sleep(2)
                else:
                    self.logger.error(f"❌ Не удалось опубликовать твит {i+1} в треде")
                    break
            
            self.logger.info(f"✅ Тред опубликован: {len(tweet_ids)} твитов")
            return tweet_ids
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка публикации треда: {e}")
            return tweet_ids
    
    def get_mentions(self, count: int = 20) -> List[Dict]:
        """Получает упоминания бота"""
        try:
            user = self.client.get_me()
            if not user.data:
                return []
            
            mentions = self.client.get_mentions(
                user_id=user.data.id,
                max_results=count,
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )
            
            if not mentions.data:
                return []
            
            result = []
            for mention in mentions.data:
                result.append({
                    'id': mention.id,
                    'text': mention.text,
                    'author_id': mention.author_id,
                    'created_at': mention.created_at,
                    'metrics': mention.public_metrics
                })
            
            self.logger.info(f"✅ Получено {len(result)} упоминаний")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения упоминаний: {e}")
            return []
    
    def get_direct_messages(self, count: int = 20) -> List[Dict]:
        """Получает прямые сообщения"""
        try:
            # Получаем DM через API v1.1
            dms = self.api_v1.get_direct_messages(count=count)
            
            result = []
            for dm in dms:
                result.append({
                    'id': dm.id,
                    'text': dm.text,
                    'sender_id': dm.sender_id,
                    'created_at': dm.created_at,
                    'sender_screen_name': dm.sender_screen_name
                })
            
            self.logger.info(f"✅ Получено {len(result)} прямых сообщений")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения DM: {e}")
            return []
    
    def reply_to_tweet(self, tweet_id: str, reply_text: str) -> Optional[str]:
        """Отвечает на твит"""
        try:
            response = self.client.create_tweet(
                text=reply_text,
                in_reply_to_tweet_id=tweet_id
            )
            
            if response.data:
                reply_id = response.data['id']
                self.logger.info(f"✅ Ответ опубликован: {reply_id}")
                return reply_id
            else:
                self.logger.error("❌ Не удалось получить ID ответа")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка ответа на твит: {e}")
            return None
    
    def send_direct_message(self, user_id: str, text: str) -> bool:
        """Отправляет прямое сообщение"""
        try:
            response = self.api_v1.send_direct_message(user_id, text)
            if response:
                self.logger.info(f"✅ DM отправлено пользователю {user_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки DM: {e}")
            return False
    
    def get_user_timeline(self, username: Optional[str] = None, count: int = 10) -> List[Dict]:
        """Получает временную шкалу пользователя"""
        try:
            if username:
                user = self.client.get_user(username=username)
                if not user.data:
                    return []
                user_id = user.data.id
            else:
                user = self.client.get_me()
                if not user.data:
                    return []
                user_id = user.data.id
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            if not tweets.data:
                return []
            
            result = []
            for tweet in tweets.data:
                result.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'metrics': tweet.public_metrics,
                    'context': tweet.context_annotations
                })
            
            self.logger.info(f"✅ Получено {len(result)} твитов из временной шкалы")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения временной шкалы: {e}")
            return []
    
    def get_trending_topics(self, woeid: int = 1) -> List[str]:
        """Получает трендовые темы (только для API v1.1)"""
        try:
            trends = self.api_v1.get_place_trends(id=woeid)
            if trends and len(trends) > 0:
                trending = [trend['name'] for trend in trends[0]['trends'] if trend['name'].startswith('#')]
                return trending[:10]  # Возвращаем топ-10 хештегов
            
            return []
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения трендов: {e}")
            return []
    
    def like_tweet(self, tweet_id: str) -> bool:
        """Лайкает твит"""
        try:
            user = self.client.get_me()
            if not user.data:
                return False
            
            response = self.client.like(tweet_id, user.data.id)
            if response.data:
                self.logger.info(f"✅ Твит {tweet_id} лайкнут")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка лайка твита: {e}")
            return False
    
    def retweet(self, tweet_id: str) -> bool:
        """Ретвитит твит"""
        try:
            user = self.client.get_me()
            if not user.data:
                return False
            
            response = self.client.retweet(tweet_id, user.data.id)
            if response.data:
                self.logger.info(f"✅ Твит {tweet_id} ретвитнут")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка ретвита: {e}")
            return False
    
    def follow_user(self, username: str) -> bool:
        """Подписывается на пользователя"""
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                return False
            
            me = self.client.get_me()
            if not me.data:
                return False
            
            response = self.client.follow_user(user.data.id, me.data.id)
            if response.data:
                self.logger.info(f"✅ Подписались на @{username}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка подписки на пользователя: {e}")
            return False
    
    def unfollow_user(self, username: str) -> bool:
        """Отписывается от пользователя"""
        try:
            user = self.client.get_user(username=username)
            if not user.data:
                return False
            
            me = self.client.get_me()
            if not me.data:
                return False
            
            response = self.client.unfollow_user(user.data.id, me.data.id)
            if response.data:
                self.logger.info(f"✅ Отписались от @{username}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка отписки от пользователя: {e}")
            return False
    
    def get_followers(self, count: int = 100) -> List[Dict]:
        """Получает список подписчиков"""
        try:
            me = self.client.get_me()
            if not me.data:
                return []
            
            followers = self.client.get_users_followers(
                id=me.data.id,
                max_results=count,
                user_fields=['username', 'name', 'public_metrics']
            )
            
            if not followers.data:
                return []
            
            result = []
            for follower in followers.data:
                result.append({
                    'id': follower.id,
                    'username': follower.username,
                    'name': follower.name,
                    'metrics': follower.public_metrics
                })
            
            self.logger.info(f"✅ Получено {len(result)} подписчиков")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения подписчиков: {e}")
            return []
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Получает информацию о пользователе"""
        try:
            user = self.client.get_user(
                username=username,
                user_fields=['name', 'description', 'public_metrics', 'verified']
            )
            
            if user.data:
                return {
                    'id': user.data.id,
                    'username': user.data.username,
                    'name': user.data.name,
                    'description': user.data.description,
                    'metrics': user.data.public_metrics,
                    'verified': user.data.verified
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения информации о пользователе: {e}")
            return None
