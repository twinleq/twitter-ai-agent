#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post Scheduler для AI Twitter Agent
Планирует и автоматически публикует посты по расписанию
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os
from .config import Config
from .twitter_client import TwitterClient
from .ai_content_generator import AIContentGenerator
from .utils import safe_json_loads, safe_json_dumps, format_timestamp

class PostScheduler:
    """Планировщик постов"""
    
    def __init__(self, config: Config, twitter_client: TwitterClient, ai_generator: AIContentGenerator):
        """Инициализация планировщика"""
        self.config = config
        self.twitter_client = twitter_client
        self.ai_generator = ai_generator
        self.logger = logging.getLogger(__name__)
        
        # Файл для хранения расписания
        self.schedule_file = './data/post_schedule.json'
        self.post_history_file = './data/post_history.json'
        
        # Создаем директорию для данных если её нет
        os.makedirs('./data', exist_ok=True)
        
        # Загружаем существующее расписание
        self.scheduled_posts = self._load_schedule()
        self.post_history = self._load_history()
        
        # Настраиваем расписание
        self._setup_schedule()
        
        self.logger.info("✅ Post Scheduler инициализирован")
    
    def _load_schedule(self) -> List[Dict]:
        """Загружает расписание постов из файла"""
        try:
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    data = safe_json_loads(f.read(), [])
                    return data if isinstance(data, list) else []
            return []
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки расписания: {e}")
            return []
    
    def _save_schedule(self):
        """Сохраняет расписание постов в файл"""
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                f.write(safe_json_dumps(self.scheduled_posts))
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения расписания: {e}")
    
    def _load_history(self) -> List[Dict]:
        """Загружает историю постов"""
        try:
            if os.path.exists(self.post_history_file):
                with open(self.post_history_file, 'r', encoding='utf-8') as f:
                    data = safe_json_loads(f.read(), [])
                    return data if isinstance(data, list) else []
            return []
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки истории: {e}")
            return []
    
    def _save_history(self):
        """Сохраняет историю постов"""
        try:
            with open(self.post_history_file, 'w', encoding='utf-8') as f:
                f.write(safe_json_dumps(self.post_history))
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения истории: {e}")
    
    def _setup_schedule(self):
        """Настраивает расписание постов"""
        if not self.config.AUTO_POSTING_ENABLED:
            return
        
        # Основное расписание постов
        schedule.every().day.at(f"{self.config.POSTING_SCHEDULE_HOUR:02d}:{self.config.POSTING_SCHEDULE_MINUTE:02d}").do(self._scheduled_post)
        
        # Дополнительные посты в течение дня
        additional_times = self._calculate_additional_post_times()
        for hour, minute in additional_times:
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._scheduled_post)
        
        self.logger.info(f"📅 Расписание настроено: основной пост в {self.config.POSTING_SCHEDULE_HOUR}:{self.config.POSTING_SCHEDULE_MINUTE:02d}")
        if additional_times:
            self.logger.info(f"📅 Дополнительные посты: {len(additional_times)} в день")
    
    def _calculate_additional_post_times(self) -> List[tuple]:
        """Вычисляет время для дополнительных постов"""
        if self.config.MAX_POSTS_PER_DAY <= 1:
            return []
        
        additional_posts = self.config.MAX_POSTS_PER_DAY - 1
        times = []
        
        # Распределяем посты равномерно в течение дня (9:00 - 21:00)
        start_hour = 9
        end_hour = 21
        total_hours = end_hour - start_hour
        
        for i in range(additional_posts):
            # Вычисляем час для поста
            hour_offset = (i + 1) * total_hours // (additional_posts + 1)
            hour = start_hour + hour_offset
            
            # Случайная минута
            minute = 0  # Можно сделать случайной: random.randint(0, 59)
            
            times.append((hour, minute))
        
        return times
    
    def _scheduled_post(self):
        """Выполняет запланированный пост"""
        try:
            # Проверяем, не превышен ли лимит постов за день
            if self._get_today_post_count() >= self.config.MAX_POSTS_PER_DAY:
                self.logger.info("📊 Лимит постов за день достигнут")
                return
            
            # Генерируем пост
            post_content = self.ai_generator.generate_post()
            if not post_content:
                self.logger.error("❌ Не удалось сгенерировать пост")
                return
            
            # Публикуем пост
            tweet_id = self.twitter_client.post_tweet(post_content)
            if tweet_id:
                # Сохраняем в историю
                self._add_to_history({
                    'id': tweet_id,
                    'content': post_content,
                    'timestamp': format_timestamp(datetime.now()),
                    'type': 'scheduled',
                    'status': 'published'
                })
                
                self.logger.info(f"✅ Запланированный пост опубликован: {tweet_id}")
            else:
                self.logger.error("❌ Не удалось опубликовать запланированный пост")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка в запланированном посте: {e}")
    
    def _get_today_post_count(self) -> int:
        """Возвращает количество постов за сегодня"""
        today = datetime.now().date()
        count = 0
        
        for post in self.post_history:
            try:
                post_date = datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S').date()
                if post_date == today and post.get('status') == 'published':
                    count += 1
            except:
                continue
        
        return count
    
    def _add_to_history(self, post_data: Dict):
        """Добавляет пост в историю"""
        self.post_history.append(post_data)
        
        # Ограничиваем историю последними 1000 постами
        if len(self.post_history) > 1000:
            self.post_history = self.post_history[-1000:]
        
        self._save_history()
    
    def schedule_custom_post(self, content: str, scheduled_time: datetime) -> bool:
        """Планирует кастомный пост на определенное время"""
        try:
            post_data = {
                'content': content,
                'scheduled_time': format_timestamp(scheduled_time),
                'created_at': format_timestamp(datetime.now()),
                'status': 'scheduled'
            }
            
            self.scheduled_posts.append(post_data)
            self._save_schedule()
            
            self.logger.info(f"📅 Кастомный пост запланирован на {format_timestamp(scheduled_time)}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка планирования кастомного поста: {e}")
            return False
    
    def schedule_thread(self, main_topic: str, thread_length: int = 3, scheduled_time: Optional[datetime] = None) -> bool:
        """Планирует публикацию треда"""
        try:
            # Генерируем тред
            tweets = self.ai_generator.generate_thread(main_topic, thread_length)
            if not tweets:
                self.logger.error("❌ Не удалось сгенерировать тред")
                return False
            
            if scheduled_time is None:
                scheduled_time = datetime.now() + timedelta(minutes=5)
            
            # Планируем каждый твит в треде
            current_time = scheduled_time
            for i, tweet_content in enumerate(tweets):
                self.schedule_custom_post(tweet_content, current_time)
                current_time += timedelta(minutes=2)  # 2 минуты между твитами
            
            self.logger.info(f"📅 Тред из {len(tweets)} твитов запланирован")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка планирования треда: {e}")
            return False
    
    def get_scheduled_posts(self) -> List[Dict]:
        """Возвращает список запланированных постов"""
        return self.scheduled_posts.copy()
    
    def get_post_history(self, days: int = 7) -> List[Dict]:
        """Возвращает историю постов за последние дни"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_posts = []
        for post in self.post_history:
            try:
                post_date = datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S')
                if post_date >= cutoff_date:
                    recent_posts.append(post)
            except:
                continue
        
        return recent_posts
    
    def cancel_scheduled_post(self, post_index: int) -> bool:
        """Отменяет запланированный пост"""
        try:
            if 0 <= post_index < len(self.scheduled_posts):
                post = self.scheduled_posts.pop(post_index)
                self._save_schedule()
                self.logger.info(f"❌ Запланированный пост отменен: {post.get('content', '')[:50]}...")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка отмены поста: {e}")
            return False
    
    def process_scheduled_posts(self):
        """Обрабатывает запланированные посты (вызывается периодически)"""
        try:
            current_time = datetime.now()
            posts_to_publish = []
            
            # Находим посты, которые пора опубликовать
            for i, post in enumerate(self.scheduled_posts):
                try:
                    scheduled_time = datetime.strptime(post['scheduled_time'], '%Y-%m-%d %H:%M:%S')
                    if scheduled_time <= current_time and post.get('status') == 'scheduled':
                        posts_to_publish.append((i, post))
                except:
                    continue
            
            # Публикуем найденные посты
            for i, post in posts_to_publish:
                tweet_id = self.twitter_client.post_tweet(post['content'])
                if tweet_id:
                    # Добавляем в историю
                    self._add_to_history({
                        'id': tweet_id,
                        'content': post['content'],
                        'timestamp': format_timestamp(datetime.now()),
                        'type': 'scheduled_custom',
                        'status': 'published'
                    })
                    
                    # Удаляем из расписания
                    self.scheduled_posts.pop(i)
                    self._save_schedule()
                    
                    self.logger.info(f"✅ Запланированный пост опубликован: {tweet_id}")
                else:
                    # Помечаем как неудачный
                    post['status'] = 'failed'
                    post['error'] = 'Failed to publish'
                    self._save_schedule()
                    
        except Exception as e:
            self.logger.error(f"❌ Ошибка обработки запланированных постов: {e}")
    
    def start(self):
        """Запускает планировщик в отдельном потоке"""
        def run_scheduler():
            while True:
                try:
                    # Обрабатываем запланированные посты
                    self.process_scheduled_posts()
                    
                    # Запускаем schedule
                    schedule.run_pending()
                    
                    # Ждем минуту
                    time.sleep(60)
                    
                except Exception as e:
                    self.logger.error(f"❌ Ошибка в планировщике: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        self.logger.info("🚀 Планировщик запущен")
    
    def stop(self):
        """Останавливает планировщик"""
        schedule.clear()
        self.logger.info("🛑 Планировщик остановлен")
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику постов"""
        total_posts = len(self.post_history)
        today_posts = self._get_today_post_count()
        scheduled_posts = len(self.scheduled_posts)
        
        # Статистика по типам постов
        post_types = {}
        for post in self.post_history:
            post_type = post.get('type', 'unknown')
            post_types[post_type] = post_types.get(post_type, 0) + 1
        
        return {
            'total_posts': total_posts,
            'today_posts': today_posts,
            'scheduled_posts': scheduled_posts,
            'post_types': post_types,
            'max_daily_posts': self.config.MAX_POSTS_PER_DAY
        }
