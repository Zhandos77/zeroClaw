#!/usr/bin/env python3
"""
Telegram бот с обработкой голосовых сообщений
Интеграция с ZeroClaw
"""

import os
import sys
import logging
import re
import telebot
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем путь к утилитам
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "utils"))

# Получаем токен из конфига
def get_bot_token():
    """Получаем токен бота из конфига"""
    try:
        with open("/root/.zeroclaw/config.toml", "r") as f:
            content = f.read()
        
        # Ищем токен в конфиге
        lines = content.split('\n')
        for line in lines:
            if '8666' in line and 'token' in line:
                match = re.search(r'"([^"]+)"', line)
                if match:
                    token = match.group(1)
                    logger.info(f"✅ Токен найден: {token[:10]}...")
                    return token
                    
        logger.error("❌ Токен не найден в конфиге")
        return None
        
    except Exception as e:
        logger.error(f"❌ Ошибка чтения конфига: {e}")
        return None

# Получаем токен
TOKEN = get_bot_token()
if not TOKEN:
    logger.error("❌ Не удалось получить токен бота")
    sys.exit(1)

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# Проверяем наличие модулей для обработки голосовых
try:
    from voice_processor import VoiceProcessor
    from telegram_voice_handler import TelegramVoiceHandler
    logger.info("✅ Модули голосовой обработки загружены")
    
    # Создаем обработчики
    voice_processor = VoiceProcessor()
    voice_handler = TelegramVoiceHandler()
    
    voice_enabled = True
except Exception as e:
    logger.warning(f"⚠️ Модули голосовой обработки недоступны: {e}")
    voice_enabled = False

# Обработчики команд
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = (
        "🤖 **ZeroClaw Telegram Bot**\n\n"
        "Я ваш персональный ИИ-ассистент!\n\n"
        "**Что я умею:**\n"
        "• Обрабатывать голосовые сообщения\n"
        "• Конвертировать валюты\n"
        "• Собирать новостные дайджесты\n"
        "• Напоминать о днях рождения\n"
        "• Помогать с кодом и разработкой\n\n"
        "**Команды:**\n"
        "/start - это сообщение\n"
        "/stt - статус распознавания речи\n"
        "/currency - курсы валют\n"
        "/news - последние новости\n"
        "/test - тестовая команда\n\n"
        "Просто отправьте голосовое сообщение или текст!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['stt'])
def stt_status(message):
    """Статус системы распознавания речи"""
    if voice_enabled:
        status_text = (
            "🔧 **Статус системы распознавания речи**\n\n"
            "✅ Vosk установлен и работает\n"
            "✅ Русская модель small-ru-0.22 загружена\n"
            "✅ Обработчик голосовых готов\n"
            "✅ Бот активен и слушает сообщения\n\n"
            "Отправьте голосовое сообщение для тестирования!"
        )
    else:
        status_text = (
            "⚠️ **Система распознавания речи отключена**\n\n"
            "Модули обработки голосовых недоступны.\n"
            "Установите зависимости:\n"
            "```bash\npip3 install vosk pydub\n```"
        )
    bot.reply_to(message, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['currency'])
def currency_command(message):
    """Курсы валют"""
    try:
        # Импортируем здесь, чтобы не падать при старте
        from skills.currency import get_currency_rates, format_currency_response
        
        # Получаем курсы для Казахстана
        rates = get_currency_rates("KZ")
        formatted = format_currency_response(rates)
        
        bot.reply_to(message, formatted, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения курсов: {e}")
        bot.reply_to(message, f"❌ Ошибка получения курсов валют: {str(e)}")

@bot.message_handler(commands=['news'])
def news_command(message):
    """Новостной дайджест"""
    try:
        # Импортируем новостной модуль
        from utils.get_news import get_news_summary
        
        bot.reply_to(message, "📰 Собираю новости...")
        
        news = get_news_summary()
        if news:
            response = "📰 **Последние новости:**\n\n"
            for item in news[:5]:  # Первые 5 новостей
                response += f"• {item['title']}\n"
                if item.get('source'):
                    response += f"  📍 {item['source']}\n"
                response += "\n"
            
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Не удалось получить новости")
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения новостей: {e}")
        bot.reply_to(message, f"❌ Ошибка получения новостей: {str(e)}")

@bot.message_handler(commands=['test'])
def test_command(message):
    """Тестовая команда"""
    bot.reply_to(message, "✅ Бот работает! Система в норме.")

# Обработка голосовых сообщений
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    """Обработка голосовых сообщений"""
    if not voice_enabled:
        bot.reply_to(message, "❌ Обработка голосовых сообщений отключена. Используйте /stt для проверки.")
        return
    
    try:
        logger.info(f"📥 Получено голосовое сообщение от {message.from_user.id}")
        
        # Отправляем статус обработки
        status_msg = bot.reply_to(message, "🔍 Обрабатываю голосовое сообщение...")
        
        # Обрабатываем голосовое
        result = voice_handler.process_voice_message(bot, message)
        
        if result.get('success'):
            text = result['text']
            confidence = result.get('confidence', 0)
            
            # Форматируем ответ
            response = (
                f"🎤 **Расшифровка голосового:**\n\n"
                f"```\n{text}\n```\n\n"
                f"**Точность:** {confidence:.1%}\n"
                f"**Длительность:** {result.get('duration', 0):.1f} сек\n"
                f"**Язык:** {result.get('language', 'ru')}"
            )
            
            # Редактируем статус сообщение
            bot.edit_message_text(
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
                text=response,
                parse_mode='Markdown'
            )
            
            logger.info(f"✅ Голосовое расшифровано: {len(text)} символов")
            
            # Теперь обрабатываем текст через ZeroClaw
            # (можно добавить интеграцию с основным ИИ)
            
        else:
            error_msg = f"❌ Ошибка обработки: {result.get('error', 'Неизвестная ошибка')}"
            bot.edit_message_text(
                chat_id=status_msg.chat.id,
                message_id=status_msg.message_id,
                text=error_msg
            )
            logger.error(f"Ошибка обработки голосового: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в обработчике голосовых: {e}")
        try:
            bot.reply_to(message, f"❌ Произошла ошибка при обработке: {str(e)}")
        except:
            pass

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Обработка текстовых сообщений"""
    if message.text.startswith('/'):
        # Игнорируем неизвестные команды
        return
    
    # Простая эхо-ответ
    response = (
        f"📝 Вы написали: *{message.text}*\n\n"
        "Я могу:\n"
        "• Расшифровать голосовое сообщение\n"
        "• Показать курсы валют (/currency)\n"
        "• Показать новости (/news)\n"
        "• Проверить статус системы (/stt)"
    )
    
    bot.reply_to(message, response, parse_mode='Markdown')

# Запуск бота
def main():
    """Основная функция"""
    print("\n" + "="*50)
    print("🤖 ZEROCLAW TELEGRAM BOT")
    print("="*50)
    print(f"Токен: {TOKEN[:10]}...")
    print(f"Обработка голосовых: {'✅ Включена' if voice_enabled else '❌ Отключена'}")
    print("\n🚀 Запускаю бота...")
    print("📱 Отправьте /start в Telegram для проверки")
    print("🎤 Отправьте голосовое сообщение для теста")
    print("🛑 Ctrl+C для остановки")
    print("="*50)
    
    try:
        bot.polling(none_stop=True, timeout=30)
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка в работе бота: {e}")

if __name__ == "__main__":
    main()