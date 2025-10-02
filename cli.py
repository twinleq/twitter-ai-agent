#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI интерфейс для AI Twitter Agent
Позволяет управлять ботом через командную строку
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.config import Config
from src.twitter_client import TwitterClient
from src.ai_content_generator import AIContentGenerator
from src.post_scheduler import PostScheduler
from src.message_handler import MessageHandler
from src.analytics import Analytics
from src.utils import setup_logging

def setup_cli():
    """Настройка CLI интерфейса"""
    parser = argparse.ArgumentParser(description='AI Twitter Agent - CLI управление')
    parser.add_argument('--config', help='Путь к файлу конфигурации')
    parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда запуска бота
    run_parser = subparsers.add_parser('run', help='Запустить бота')
    run_parser.add_argument('--daemon', action='store_true', help='Запуск в фоновом режиме')
    
    # Команда генерации поста
    post_parser = subparsers.add_parser('post', help='Создать и опубликовать пост')
    post_parser.add_argument('--topic', help='Тема поста')
    post_parser.add_argument('--dry-run', action='store_true', help='Только сгенерировать, не публиковать')
    post_parser.add_argument('--thread', type=int, help='Создать тред из N твитов')
    
    # Команда планирования
    schedule_parser = subparsers.add_parser('schedule', help='Управление расписанием')
    schedule_parser.add_argument('--list', action='store_true', help='Показать запланированные посты')
    schedule_parser.add_argument('--add', help='Добавить пост в расписание')
    schedule_parser.add_argument('--time', help='Время публикации (YYYY-MM-DD HH:MM)')
    schedule_parser.add_argument('--cancel', type=int, help='Отменить пост по индексу')
    
    # Команда аналитики
    analytics_parser = subparsers.add_parser('analytics', help='Показать аналитику')
    analytics_parser.add_argument('--days', type=int, default=7, help='Количество дней для анализа')
    analytics_parser.add_argument('--export', help='Экспорт в файл (JSON/CSV)')
    
    # Команда ответов
    response_parser = subparsers.add_parser('response', help='Управление ответами')
    response_parser.add_argument('--reply', help='Ответить на твит по ID')
    response_parser.add_argument('--text', help='Текст ответа')
    response_parser.add_argument('--stats', action='store_true', help='Статистика ответов')
    
    # Команда конфигурации
    config_parser = subparsers.add_parser('config', help='Управление конфигурацией')
    config_parser.add_argument('--show', action='store_true', help='Показать текущую конфигурацию')
    config_parser.add_argument('--validate', action='store_true', help='Проверить конфигурацию')
    config_parser.add_argument('--test-api', action='store_true', help='Тестировать API подключения')
    
    # Команда утилит
    utils_parser = subparsers.add_parser('utils', help='Утилиты')
    utils_parser.add_argument('--backup', help='Создать резервную копию данных')
    utils_parser.add_argument('--restore', help='Восстановить из резервной копии')
    utils_parser.add_argument('--clean', action='store_true', help='Очистить старые данные')
    
    return parser

def run_bot(args):
    """Запуск бота"""
    print("🚀 Запуск AI Twitter Agent...")
    
    # Загружаем конфигурацию
    load_dotenv()
    config = Config()
    
    # Настраиваем логирование
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level, config.LOG_FILE)
    
    # Импортируем main функцию
    from main import main
    
    if args.daemon:
        print("🔄 Запуск в фоновом режиме...")
        # Здесь можно добавить daemon логику
        main()
    else:
        main()

def create_post(args):
    """Создание и публикация поста"""
    print("📝 Создание поста...")
    
    load_dotenv()
    config = Config()
    setup_logging('INFO')
    
    # Инициализируем компоненты
    twitter_client = TwitterClient(config)
    ai_generator = AIContentGenerator(config)
    
    try:
        if args.thread:
            # Создаем тред
            tweets = ai_generator.generate_thread(args.topic or 'programming', args.thread)
            if tweets:
                print(f"✅ Сгенерирован тред из {len(tweets)} твитов:")
                for i, tweet in enumerate(tweets, 1):
                    print(f"\n{i}/{len(tweets)}: {tweet}")
                
                if not args.dry_run:
                    tweet_ids = twitter_client.post_thread(tweets)
                    print(f"✅ Тред опубликован: {len(tweet_ids)} твитов")
            else:
                print("❌ Не удалось сгенерировать тред")
        else:
            # Создаем обычный пост
            post = ai_generator.generate_post(args.topic)
            if post:
                print(f"✅ Сгенерирован пост:\n{post}")
                
                if not args.dry_run:
                    tweet_id = twitter_client.post_tweet(post)
                    if tweet_id:
                        print(f"✅ Пост опубликован: {tweet_id}")
                    else:
                        print("❌ Не удалось опубликовать пост")
            else:
                print("❌ Не удалось сгенерировать пост")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def manage_schedule(args):
    """Управление расписанием"""
    print("📅 Управление расписанием...")
    
    load_dotenv()
    config = Config()
    setup_logging('INFO')
    
    twitter_client = TwitterClient(config)
    ai_generator = AIContentGenerator(config)
    scheduler = PostScheduler(config, twitter_client, ai_generator)
    
    try:
        if args.list:
            posts = scheduler.get_scheduled_posts()
            if posts:
                print(f"\n📋 Запланированные посты ({len(posts)}):")
                for i, post in enumerate(posts):
                    print(f"{i}: {post['scheduled_time']} - {post['content'][:50]}...")
            else:
                print("📋 Нет запланированных постов")
        
        elif args.add:
            if not args.time:
                print("❌ Укажите время публикации с помощью --time")
                return
            
            try:
                scheduled_time = datetime.strptime(args.time, '%Y-%m-%d %H:%M')
                success = scheduler.schedule_custom_post(args.add, scheduled_time)
                if success:
                    print(f"✅ Пост запланирован на {scheduled_time}")
                else:
                    print("❌ Не удалось запланировать пост")
            except ValueError:
                print("❌ Неверный формат времени. Используйте: YYYY-MM-DD HH:MM")
        
        elif args.cancel is not None:
            success = scheduler.cancel_scheduled_post(args.cancel)
            if success:
                print(f"✅ Пост {args.cancel} отменен")
            else:
                print(f"❌ Не удалось отменить пост {args.cancel}")
        
        else:
            print("❌ Укажите действие: --list, --add или --cancel")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def show_analytics(args):
    """Показ аналитики"""
    print(f"📊 Аналитика за {args.days} дней...")
    
    load_dotenv()
    config = Config()
    setup_logging('INFO')
    
    analytics = Analytics(config)
    
    try:
        # Получаем аналитику
        post_analytics = analytics.get_post_analytics(args.days)
        response_analytics = analytics.get_response_analytics(args.days)
        daily_stats = analytics.get_daily_stats(args.days)
        
        # Выводим отчет
        report = analytics.generate_report(args.days)
        print(report)
        
        # Экспорт если нужно
        if args.export:
            data = {
                'post_analytics': post_analytics,
                'response_analytics': response_analytics,
                'daily_stats': daily_stats,
                'generated_at': datetime.now().isoformat()
            }
            
            if args.export.endswith('.json'):
                with open(args.export, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif args.export.endswith('.csv'):
                # Здесь можно добавить экспорт в CSV
                print(f"📁 Экспорт в CSV пока не реализован")
            
            print(f"✅ Данные экспортированы в {args.export}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def manage_responses(args):
    """Управление ответами"""
    print("💬 Управление ответами...")
    
    load_dotenv()
    config = Config()
    setup_logging('INFO')
    
    twitter_client = TwitterClient(config)
    ai_generator = AIContentGenerator(config)
    message_handler = MessageHandler(config, twitter_client, ai_generator)
    
    try:
        if args.reply and args.text:
            success = message_handler.manual_response(args.reply, args.text)
            if success:
                print(f"✅ Ответ отправлен на твит {args.reply}")
            else:
                print(f"❌ Не удалось отправить ответ")
        
        elif args.stats:
            stats = message_handler.get_response_statistics()
            print(f"\n📊 Статистика ответов:")
            print(f"• Всего ответов: {stats['total_responses']}")
            print(f"• За 24 часа: {stats['recent_responses_24h']}")
            print(f"• Обработано упоминаний: {stats['processed_mentions']}")
            print(f"• Обработано DM: {stats['processed_dms']}")
            
            if stats['message_types']:
                print(f"\n📝 Типы сообщений:")
                for msg_type, count in stats['message_types'].items():
                    print(f"• {msg_type}: {count}")
        
        else:
            print("❌ Укажите действие: --reply с --text или --stats")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def manage_config(args):
    """Управление конфигурацией"""
    print("⚙️ Управление конфигурацией...")
    
    load_dotenv()
    config = Config()
    
    try:
        if args.show:
            print(f"\n📋 Текущая конфигурация:")
            config_dict = config.to_dict()
            for key, value in config_dict.items():
                print(f"• {key}: {value}")
        
        elif args.validate:
            if config.validate():
                print("✅ Конфигурация корректна")
            else:
                print("❌ Конфигурация содержит ошибки")
        
        elif args.test_api:
            print("🔌 Тестирование API подключений...")
            
            # Тестируем Twitter API
            twitter_client = TwitterClient(config)
            if twitter_client.verify_credentials():
                print("✅ Twitter API подключение успешно")
            else:
                print("❌ Ошибка подключения к Twitter API")
            
            # Тестируем OpenAI API
            ai_generator = AIContentGenerator(config)
            test_post = ai_generator.generate_post("test")
            if test_post:
                print("✅ OpenAI API подключение успешно")
            else:
                print("❌ Ошибка подключения к OpenAI API")
        
        else:
            print("❌ Укажите действие: --show, --validate или --test-api")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def manage_utils(args):
    """Утилиты"""
    print("🛠 Утилиты...")
    
    try:
        if args.backup:
            # Создание резервной копии
            import shutil
            import os
            from datetime import datetime
            
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # Копируем данные
            if os.path.exists('./data'):
                shutil.copytree('./data', f'{backup_dir}/data')
            
            if os.path.exists('./logs'):
                shutil.copytree('./logs', f'{backup_dir}/logs')
            
            print(f"✅ Резервная копия создана: {backup_dir}")
        
        elif args.restore:
            # Восстановление из резервной копии
            import shutil
            import os
            
            if os.path.exists(args.restore):
                if os.path.exists(f'{args.restore}/data'):
                    shutil.copytree(f'{args.restore}/data', './data', dirs_exist_ok=True)
                if os.path.exists(f'{args.restore}/logs'):
                    shutil.copytree(f'{args.restore}/logs', './logs', dirs_exist_ok=True)
                print(f"✅ Данные восстановлены из {args.restore}")
            else:
                print(f"❌ Резервная копия {args.restore} не найдена")
        
        elif args.clean:
            # Очистка старых данных
            import os
            import glob
            
            # Очищаем старые логи (старше 30 дней)
            log_files = glob.glob('./logs/*.log*')
            for log_file in log_files:
                if os.path.getmtime(log_file) < (datetime.now().timestamp() - 30 * 24 * 3600):
                    os.remove(log_file)
                    print(f"🗑 Удален старый лог: {log_file}")
            
            print("✅ Очистка завершена")
        
        else:
            print("❌ Укажите действие: --backup, --restore или --clean")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Главная функция CLI"""
    parser = setup_cli()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'run':
            run_bot(args)
        elif args.command == 'post':
            create_post(args)
        elif args.command == 'schedule':
            manage_schedule(args)
        elif args.command == 'analytics':
            show_analytics(args)
        elif args.command == 'response':
            manage_responses(args)
        elif args.command == 'config':
            manage_config(args)
        elif args.command == 'utils':
            manage_utils(args)
        else:
            print(f"❌ Неизвестная команда: {args.command}")
            
    except KeyboardInterrupt:
        print("\n🛑 Операция прервана пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
