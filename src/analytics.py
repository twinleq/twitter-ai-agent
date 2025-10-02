#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analytics для AI Twitter Agent
Собирает и анализирует метрики работы бота
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os
from .config import Config
from .twitter_client import TwitterClient
from .utils import calculate_engagement_score, format_timestamp, safe_json_dumps

class Analytics:
    """Система аналитики и мониторинга"""
    
    def __init__(self, config: Config, twitter_client: Optional[TwitterClient] = None):
        """Инициализация системы аналитики"""
        self.config = config
        self.twitter_client = twitter_client
        self.logger = logging.getLogger(__name__)
        
        # Путь к базе данных
        self.db_path = config.ANALYTICS_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Инициализация базы данных
        self._init_database()
        
        self.logger.info("✅ Analytics инициализирована")
    
    def _init_database(self):
        """Инициализирует базу данных для аналитики"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица метрик постов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS post_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tweet_id TEXT UNIQUE,
                        content TEXT,
                        created_at TIMESTAMP,
                        likes INTEGER DEFAULT 0,
                        retweets INTEGER DEFAULT 0,
                        replies INTEGER DEFAULT 0,
                        quotes INTEGER DEFAULT 0,
                        impressions INTEGER DEFAULT 0,
                        engagement_rate REAL DEFAULT 0.0,
                        topic TEXT,
                        post_type TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица метрик ответов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS response_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        response_id TEXT UNIQUE,
                        original_tweet_id TEXT,
                        user_id TEXT,
                        response_type TEXT,
                        message_type TEXT,
                        response_content TEXT,
                        created_at TIMESTAMP,
                        likes INTEGER DEFAULT 0,
                        retweets INTEGER DEFAULT 0,
                        replies INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица метрик пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE,
                        username TEXT,
                        followers_count INTEGER DEFAULT 0,
                        following_count INTEGER DEFAULT 0,
                        tweets_count INTEGER DEFAULT 0,
                        verified BOOLEAN DEFAULT FALSE,
                        last_interaction TIMESTAMP,
                        interaction_count INTEGER DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица общей статистики
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE UNIQUE,
                        posts_published INTEGER DEFAULT 0,
                        responses_sent INTEGER DEFAULT 0,
                        new_followers INTEGER DEFAULT 0,
                        total_likes INTEGER DEFAULT 0,
                        total_retweets INTEGER DEFAULT 0,
                        total_replies INTEGER DEFAULT 0,
                        avg_engagement_rate REAL DEFAULT 0.0,
                        top_topic TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                self.logger.info("✅ База данных аналитики инициализирована")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации базы данных: {e}")
    
    def track_post(self, tweet_id: str, content: str, topic: str = None, post_type: str = 'scheduled'):
        """Отслеживает новый пост"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO post_metrics 
                    (tweet_id, content, created_at, topic, post_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (tweet_id, content, datetime.now(), topic, post_type))
                
                conn.commit()
                self.logger.info(f"✅ Пост {tweet_id} добавлен в аналитику")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка отслеживания поста: {e}")
    
    def track_response(self, response_id: str, original_tweet_id: str, user_id: str, 
                      response_type: str, message_type: str, content: str):
        """Отслеживает новый ответ"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO response_metrics 
                    (response_id, original_tweet_id, user_id, response_type, 
                     message_type, response_content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (response_id, original_tweet_id, user_id, response_type, 
                      message_type, content, datetime.now()))
                
                # Обновляем метрики пользователя
                self._update_user_interaction(user_id)
                
                conn.commit()
                self.logger.info(f"✅ Ответ {response_id} добавлен в аналитику")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка отслеживания ответа: {e}")
    
    def update_post_metrics(self, tweet_id: str, metrics: Dict):
        """Обновляет метрики поста"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Вычисляем engagement rate
                total_engagement = (
                    metrics.get('like_count', 0) + 
                    metrics.get('retweet_count', 0) * 2 + 
                    metrics.get('reply_count', 0) * 3
                )
                
                # Предполагаем количество подписчиков (можно получить из API)
                followers = metrics.get('followers_count', 1000)
                engagement_rate = (total_engagement / followers * 100) if followers > 0 else 0
                
                cursor.execute('''
                    UPDATE post_metrics SET
                        likes = ?,
                        retweets = ?,
                        replies = ?,
                        quotes = ?,
                        impressions = ?,
                        engagement_rate = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE tweet_id = ?
                ''', (
                    metrics.get('like_count', 0),
                    metrics.get('retweet_count', 0),
                    metrics.get('reply_count', 0),
                    metrics.get('quote_count', 0),
                    metrics.get('impression_count', 0),
                    engagement_rate,
                    tweet_id
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления метрик поста: {e}")
    
    def update_response_metrics(self, response_id: str, metrics: Dict):
        """Обновляет метрики ответа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE response_metrics SET
                        likes = ?,
                        retweets = ?,
                        replies = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE response_id = ?
                ''', (
                    metrics.get('like_count', 0),
                    metrics.get('retweet_count', 0),
                    metrics.get('reply_count', 0),
                    response_id
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления метрик ответа: {e}")
    
    def _update_user_interaction(self, user_id: str):
        """Обновляет статистику взаимодействий с пользователем"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_metrics 
                    (user_id, last_interaction, interaction_count)
                    VALUES (?, ?, COALESCE((SELECT interaction_count FROM user_metrics WHERE user_id = ?), 0) + 1)
                ''', (user_id, datetime.now(), user_id))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления взаимодействий пользователя: {e}")
    
    def update_user_info(self, user_id: str, username: str, user_data: Dict):
        """Обновляет информацию о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_metrics 
                    (user_id, username, followers_count, following_count, 
                     tweets_count, verified, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    user_id,
                    username,
                    user_data.get('followers_count', 0),
                    user_data.get('following_count', 0),
                    user_data.get('tweet_count', 0),
                    user_data.get('verified', False)
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления информации о пользователе: {e}")
    
    def update_daily_stats(self, date: datetime = None):
        """Обновляет ежедневную статистику"""
        try:
            if date is None:
                date = datetime.now()
            
            date_str = date.strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем статистику за день
                cursor.execute('''
                    SELECT 
                        COUNT(*) as posts_published,
                        AVG(engagement_rate) as avg_engagement_rate,
                        topic,
                        SUM(likes) as total_likes,
                        SUM(retweets) as total_retweets,
                        SUM(replies) as total_replies
                    FROM post_metrics 
                    WHERE DATE(created_at) = ?
                    GROUP BY topic
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ''', (date_str,))
                
                result = cursor.fetchone()
                if result:
                    posts_published, avg_engagement, top_topic, total_likes, total_retweets, total_replies = result
                else:
                    posts_published = avg_engagement = total_likes = total_retweets = total_replies = 0
                    top_topic = None
                
                # Получаем количество ответов за день
                cursor.execute('''
                    SELECT COUNT(*) FROM response_metrics 
                    WHERE DATE(created_at) = ?
                ''', (date_str,))
                
                responses_sent = cursor.fetchone()[0] or 0
                
                # Сохраняем статистику
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_stats 
                    (date, posts_published, responses_sent, total_likes, 
                     total_retweets, total_replies, avg_engagement_rate, top_topic)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date_str, posts_published, responses_sent, total_likes, 
                      total_retweets, total_replies, avg_engagement or 0, top_topic))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления ежедневной статистики: {e}")
    
    def update_metrics(self):
        """Обновляет все метрики (вызывается периодически)"""
        try:
            if not self.twitter_client:
                return
            
            # Обновляем метрики постов
            self._update_posts_metrics()
            
            # Обновляем метрики ответов
            self._update_responses_metrics()
            
            # Обновляем ежедневную статистику
            self.update_daily_stats()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления метрик: {e}")
    
    def _update_posts_metrics(self):
        """Обновляет метрики постов через Twitter API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем посты за последние 7 дней
                cursor.execute('''
                    SELECT tweet_id FROM post_metrics 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                
                tweet_ids = [row[0] for row in cursor.fetchall()]
                
                for tweet_id in tweet_ids:
                    try:
                        # Получаем метрики из Twitter API
                        tweet = self.twitter_client.client.get_tweet(
                            tweet_id, 
                            tweet_fields=['public_metrics']
                        )
                        
                        if tweet.data:
                            metrics = tweet.data.public_metrics
                            self.update_post_metrics(tweet_id, metrics)
                            
                    except Exception as e:
                        self.logger.warning(f"⚠️ Не удалось обновить метрики для поста {tweet_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления метрик постов: {e}")
    
    def _update_responses_metrics(self):
        """Обновляет метрики ответов через Twitter API"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем ответы за последние 7 дней
                cursor.execute('''
                    SELECT response_id FROM response_metrics 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                
                response_ids = [row[0] for row in cursor.fetchall()]
                
                for response_id in response_ids:
                    try:
                        # Получаем метрики из Twitter API
                        tweet = self.twitter_client.client.get_tweet(
                            response_id,
                            tweet_fields=['public_metrics']
                        )
                        
                        if tweet.data:
                            metrics = tweet.data.public_metrics
                            self.update_response_metrics(response_id, metrics)
                            
                    except Exception as e:
                        self.logger.warning(f"⚠️ Не удалось обновить метрики для ответа {response_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления метрик ответов: {e}")
    
    def get_post_analytics(self, days: int = 7) -> Dict:
        """Возвращает аналитику постов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общая статистика постов
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(engagement_rate) as avg_engagement,
                        SUM(likes) as total_likes,
                        SUM(retweets) as total_retweets,
                        SUM(replies) as total_replies,
                        MAX(engagement_rate) as best_engagement
                    FROM post_metrics 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days))
                
                result = cursor.fetchone()
                if result:
                    total_posts, avg_engagement, total_likes, total_retweets, total_replies, best_engagement = result
                else:
                    total_posts = avg_engagement = total_likes = total_retweets = total_replies = best_engagement = 0
                
                # Топ посты по вовлеченности
                cursor.execute('''
                    SELECT tweet_id, content, engagement_rate, likes, retweets, replies
                    FROM post_metrics 
                    WHERE created_at >= datetime('now', '-{} days')
                    ORDER BY engagement_rate DESC
                    LIMIT 5
                '''.format(days))
                
                top_posts = []
                for row in cursor.fetchall():
                    top_posts.append({
                        'tweet_id': row[0],
                        'content': row[1][:100] + '...' if len(row[1]) > 100 else row[1],
                        'engagement_rate': row[2],
                        'likes': row[3],
                        'retweets': row[4],
                        'replies': row[5]
                    })
                
                # Статистика по темам
                cursor.execute('''
                    SELECT topic, COUNT(*) as count, AVG(engagement_rate) as avg_engagement
                    FROM post_metrics 
                    WHERE created_at >= datetime('now', '-{} days') AND topic IS NOT NULL
                    GROUP BY topic
                    ORDER BY avg_engagement DESC
                '''.format(days))
                
                topic_stats = []
                for row in cursor.fetchall():
                    topic_stats.append({
                        'topic': row[0],
                        'count': row[1],
                        'avg_engagement': row[2]
                    })
                
                return {
                    'total_posts': total_posts,
                    'avg_engagement_rate': round(avg_engagement or 0, 2),
                    'total_likes': total_likes,
                    'total_retweets': total_retweets,
                    'total_replies': total_replies,
                    'best_engagement_rate': round(best_engagement or 0, 2),
                    'top_posts': top_posts,
                    'topic_stats': topic_stats
                }
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения аналитики постов: {e}")
            return {}
    
    def get_response_analytics(self, days: int = 7) -> Dict:
        """Возвращает аналитику ответов"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общая статистика ответов
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_responses,
                        COUNT(DISTINCT user_id) as unique_users,
                        SUM(likes) as total_likes,
                        SUM(retweets) as total_retweets,
                        SUM(replies) as total_replies
                    FROM response_metrics 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days))
                
                result = cursor.fetchone()
                if result:
                    total_responses, unique_users, total_likes, total_retweets, total_replies = result
                else:
                    total_responses = unique_users = total_likes = total_retweets = total_replies = 0
                
                # Статистика по типам сообщений
                cursor.execute('''
                    SELECT message_type, COUNT(*) as count
                    FROM response_metrics 
                    WHERE created_at >= datetime('now', '-{} days')
                    GROUP BY message_type
                    ORDER BY count DESC
                '''.format(days))
                
                message_type_stats = []
                for row in cursor.fetchall():
                    message_type_stats.append({
                        'type': row[0],
                        'count': row[1]
                    })
                
                return {
                    'total_responses': total_responses,
                    'unique_users': unique_users,
                    'total_likes': total_likes,
                    'total_retweets': total_retweets,
                    'total_replies': total_replies,
                    'message_type_stats': message_type_stats
                }
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения аналитики ответов: {e}")
            return {}
    
    def get_daily_stats(self, days: int = 30) -> List[Dict]:
        """Возвращает ежедневную статистику"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT date, posts_published, responses_sent, total_likes, 
                           total_retweets, total_replies, avg_engagement_rate, top_topic
                    FROM daily_stats 
                    WHERE date >= date('now', '-{} days')
                    ORDER BY date DESC
                '''.format(days))
                
                stats = []
                for row in cursor.fetchall():
                    stats.append({
                        'date': row[0],
                        'posts_published': row[1],
                        'responses_sent': row[2],
                        'total_likes': row[3],
                        'total_retweets': row[4],
                        'total_replies': row[5],
                        'avg_engagement_rate': round(row[6] or 0, 2),
                        'top_topic': row[7]
                    })
                
                return stats
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения ежедневной статистики: {e}")
            return []
    
    def generate_report(self, days: int = 7) -> str:
        """Генерирует текстовый отчет"""
        try:
            post_analytics = self.get_post_analytics(days)
            response_analytics = self.get_response_analytics(days)
            daily_stats = self.get_daily_stats(days)
            
            report = f"""
📊 ОТЧЕТ AI TWITTER AGENT за {days} дней
{'='*50}

📝 ПОСТЫ:
• Всего опубликовано: {post_analytics.get('total_posts', 0)}
• Средняя вовлеченность: {post_analytics.get('avg_engagement_rate', 0)}%
• Всего лайков: {post_analytics.get('total_likes', 0)}
• Всего ретвитов: {post_analytics.get('total_retweets', 0)}
• Всего ответов: {post_analytics.get('total_replies', 0)}

💬 ОТВЕТЫ:
• Всего ответов: {response_analytics.get('total_responses', 0)}
• Уникальных пользователей: {response_analytics.get('unique_users', 0)}
• Лайков на ответы: {response_analytics.get('total_likes', 0)}
• Ретвитов ответов: {response_analytics.get('total_retweets', 0)}

🏆 ТОП ТЕМЫ:
"""
            
            for topic in post_analytics.get('topic_stats', [])[:3]:
                report += f"• {topic['topic']}: {topic['count']} постов, {topic['avg_engagement']:.1f}% вовлеченность\n"
            
            report += f"\n📈 ЕЖЕДНЕВНАЯ АКТИВНОСТЬ:\n"
            for day in daily_stats[:7]:  # Показываем последние 7 дней
                report += f"• {day['date']}: {day['posts_published']} постов, {day['responses_sent']} ответов\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка генерации отчета: {e}")
            return "❌ Ошибка генерации отчета"
