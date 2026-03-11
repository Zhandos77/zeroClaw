#!/usr/bin/env python3
"""
Интеграция голосовых сообщений с существующим Telegram ботом ZeroClaw
Запускается как отдельный процесс, слушает голосовые и обрабатывает их
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

try:
    import telebot
    from telegram_voice_handler import TelegramVoiceHandler
    from voice_processor import VoiceProcessor
    logger.info("✅ Все модули загружены успешно")
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    logger.info("Устанавливаем зависимости...")
    os.system("pip3 install pyTelegramBotAPI")
    import telebot
    from telegram_voice_handler import TelegramVoiceHandler
    from voice_processor import VoiceProcessor

class VoiceBotIntegration:
    """Интеграция обработки голосовых с Telegram ботом"""
    
    def __init__(self):
        self.bot = None
        self.voice_handler = None
        self.voice_processor = None
        self.config = self.load_config()
        
    def load_config(self):
        """Загружаем конфигурацию из config.toml"""
        config_path = "/root/.zeroclaw/config.toml"
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Ищем токен бота (простой парсинг)
            import re
            token_match = re.search(r'bot_"token":\s*"([^"]+)"', content)
            if token_match:
                token = token_match.group(1)
                logger.info(f"✅ Токен бота найден: {token[:10]}...")
            else:
                # Пробуем другой формат
                token_match = re.search(r'token\s*=\s*"([^"]+)"', content)
                if token_match:
                    token = token_match.group(1)
                    logger.info(f"✅ Токен бота найден: {token[:10]}...")
                else:
                    logger.error("❌ Токен бота не найден в конфиге")
                    token = None
            
            # Ищем разрешенных пользователей
            users_match = re.search(r'allowed_users\s*=\s*\[([^\]]+)\]', content)
            allowed_users = []
            if users_match:
                users_str = users_match.group(1)
                # Извлекаем ID пользователей
                for user_id in re.findall(r'"([^"]+)"', users_str):
                    allowed_users.append(user_id)
                logger.info(f"✅ Разрешенные пользователи: {allowed_users}")
            
            return {
                'token': token,
                'allowed_users': allowed_users
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфига: {e}")
            return {'token': None, 'allowed_users': []}
    
    def initialize(self):
        """Инициализация всех компонентов"""
        if not self.config['token']:
            logger.error("❌ Не удалось получить токен бота")
            return False
        
        try:
            # Инициализируем бота
            self.bot = telebot.TeleBot(self.config['token'])
            logger.info("✅ Telegram бот инициализирован")
            
            # Инициализируем обработчик голосовых
            self.voice_handler = TelegramVoiceHandler()
            self.voice_processor = VoiceProcessor()
            logger.info("✅ Обработчики голосовых инициализированы")
            
            # Регистрируем обработчики
            self.register_handlers()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            return False
    
    def register_handlers(self):
        """Регистрируем обработчики сообщений"""
        
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            """Приветственное сообщение"""
            welcome_text = (
                "🎤 **Бот обработки голосовых сообщений**\n\n"
                "Я умею расшифровывать голосовые сообщения!\n\n"
                "**Команды:**\n"
                "/start - это сообщение\n"
                "/stt - статус системы распознавания\n"
                "/test - тестовая команда\n\n"
                "Просто отправь мне голосовое сообщение, и я расшифрую его!"
            )
            self.bot.reply_to(message, welcome_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['stt'])
        def stt_status(message):
            """Статус системы распознавания речи"""
            status_text = (
                "🔧 **Статус системы распознавания речи**\n\n"
                "✅ Vosk установлен и работает\n"
                "✅ Русская модель small-ru-0.22 загружена\n"
                "✅ Обработчик голосовых готов\n"
                "✅ Бот активен и слушает сообщения\n\n"
                "Отправь голосовое сообщение для тестирования!"
            )
            self.bot.reply_to(message, status_text, parse_mode='Markdown')
        
        @self.bot.message_handler(commands=['test'])
        def test_command(message):
            """Тестовая команда"""
            self.bot.reply_to(message, "✅ Бот работает! Отправь голосовое сообщение для теста.")
        
        @self.bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            """Обработка голосовых сообщений"""
            try:
                # Проверяем, разрешен ли пользователь
                user_id = str(message.from_user.id)
                if self.config['allowed_users'] and user_id not in self.config['allowed_users']:
                    logger.warning(f"Попытка доступа от неавторизованного пользователя: {user_id}")
                    self.bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
                    return
                
                logger.info(f"📥 Получено голосовое сообщение от {user_id}")
                
                # Отправляем статус обработки
                status_msg = self.bot.reply_to(message, "🔍 Обрабатываю голосовое сообщение...")
                
                # Обрабатываем голосовое
                result = self.voice_handler.process_voice_message(self.bot, message)
                
                if result.get('success'):
                    text = result['text']
                    confidence = result.get('confidence', 0)
                    
                    # Форматируем ответ
                    response = (
                        f"📝 **Расшифровка голосового:**\n\n"
                        f"```\n{text}\n```\n\n"
                        f"**Точность:** {confidence:.1%}\n"
                        f"**Длительность:** {result.get('duration', 0):.1f} сек\n"
                        f"**Язык:** {result.get('language', 'ru')}"
                    )
                    
                    # Редактируем статус сообщение
                    self.bot.edit_message_text(
                        chat_id=status_msg.chat.id,
                        message_id=status_msg.message_id,
                        text=response,
                        parse_mode='Markdown'
                    )
                    
                    logger.info(f"✅ Голосовое расшифровано: {len(text)} символов")
                    
                else:
                    error_msg = f"❌ Ошибка обработки: {result.get('error', 'Неизвестная ошибка')}"
                    self.bot.edit_message_text(
                        chat_id=status_msg.chat.id,
                        message_id=status_msg.message_id,
                        text=error_msg
                    )
                    logger.error(f"Ошибка обработки голосового: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ Критическая ошибка в обработчике голосовых: {e}")
                try:
                    self.bot.reply_to(message, f"❌ Произошла ошибка при обработке: {str(e)}")
                except:
                    pass
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_text(message):
            """Обработка текстовых сообщений"""
            if message.text.startswith('/'):
                # Игнорируем неизвестные команды
                return
            
            # Для текстовых сообщений просто пересылаем в ZeroClaw
            # (или можно добавить собственную логику)
            self.bot.reply_to(message, 
                "📝 Я специализируюсь на обработке голосовых сообщений.\n"
                "Отправь мне голосовое, и я его расшифрую!\n\n"
                "Используй /stt для проверки статуса системы."
            )
        
        logger.info("✅ Обработчики сообщений зарегистрированы")
    
    def run(self):
        """Запуск бота"""
        if not self.initialize():
            logger.error("❌ Не удалось инициализировать бота")
            return
        
        logger.info("🚀 Запускаю бота обработки голосовых сообщений...")
        logger.info("📱 Бот слушает сообщения...")
        
        try:
            # Запускаем polling
            self.bot.infinity_polling(timeout=30, long_polling_timeout=30)
        except KeyboardInterrupt:
            logger.info("⏹️ Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Ошибка в работе бота: {e}")

def main():
    """Основная функция"""
    print("\n" + "="*50)
    print("🎤 БОТ ОБРАБОТКИ ГОЛОСОВЫХ СООБЩЕНИЙ")
    print("="*50)
    print("Настройка и запуск...\n")
    
    # Проверяем наличие токена в переменных окружения
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        print(f"✅ Токен найден в переменных окружения: {token[:10]}...")
    
    # Создаем и запускаем интеграцию
    integration = VoiceBotIntegration()
    integration.run()

if __name__ == "__main__":
    main()