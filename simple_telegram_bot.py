#!/usr/bin/env python3
"""
Простой Telegram бот для ZeroClaw
Без сложной обработки голосовых - только базовые функции
"""

import os
import sys
import re
import logging
import telebot
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Получаем токен из конфига
def get_bot_token():
    """Получаем токен бота из конфига"""
    try:
        with open("/root/.zeroclaw/config.toml", "r") as f:
            content = f.read()
        
        # Ищем токен в конфиге
        for line in content.split('\n'):
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

# Команда /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = (
        "🤖 **ZeroClaw Telegram Bot**\n\n"
        "Я ваш персональный ИИ-ассистент!\n\n"
        "**Что я умею:**\n"
        "• Отвечать на сообщения\n"
        "• Показывать курсы валют\n" 
        "• Интегрироваться с ZeroClaw\n\n"
        "**Команды:**\n"
        "/start - это сообщение\n"
        "/currency - курсы валют\n"
        "/status - статус системы\n"
        "/echo <текст> - эхо-ответ\n\n"
        "Бот работает и готов к использованию!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# Команда /currency
@bot.message_handler(commands=['currency'])
def currency_command(message):
    """Курсы валют"""
    try:
        # Добавляем путь к skills
        sys.path.insert(0, '/root/.zeroclaw/workspace')
        
        from skills.currency import get_currency_rates
        
        # Получаем курсы для Казахстана
        rates = get_currency_rates("KZ")
        
        if rates and 'rates' in rates:
            response = "💱 **Курсы валют (НБ РК):**\n\n"
            response += f"📅 Дата: {rates.get('date', 'N/A')}\n"
            response += f"🏦 Источник: {rates.get('source', 'НБ РК')}\n\n"
            
            for currency, rate in rates['rates'].items():
                response += f"• 1 USD = {rate} {currency}\n"
            
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Не удалось получить курсы валют")
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения курсов: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

# Команда /status
@bot.message_handler(commands=['status'])
def status_command(message):
    """Статус системы"""
    import platform
    import datetime
    
    status_text = (
        "🔧 **Статус системы:**\n\n"
        f"🤖 Бот: ✅ Работает\n"
        f"📅 Время: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"💻 Система: {platform.system()} {platform.release()}\n"
        f"🐍 Python: {platform.python_version()}\n"
        f"📱 Ваш ID: {message.from_user.id}\n\n"
        "Все системы работают в штатном режиме!"
    )
    bot.reply_to(message, status_text, parse_mode='Markdown')

# Команда /echo
@bot.message_handler(commands=['echo'])
def echo_command(message):
    """Эхо-команда"""
    text = message.text[6:].strip()  # Убираем "/echo "
    if text:
        bot.reply_to(message, f"📣 Эхо: *{text}*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Использование: /echo <текст>")

# Обработка всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    if message.text.startswith('/'):
        # Неизвестная команда
        bot.reply_to(message, "❌ Неизвестная команда. Используйте /start для списка команд.")
        return
    
    # Простой ответ на любой текст
    response = (
        f"📝 Вы написали: *{message.text}*\n\n"
        "Я могу:\n"
        "• Показать курсы валют (/currency)\n"
        "• Показать статус системы (/status)\n"
        "• Отправить эхо (/echo текст)\n\n"
        "Или просто продолжайте общаться!"
    )
    
    bot.reply_to(message, response, parse_mode='Markdown')

# Основная функция
def main():
    """Запуск бота"""
    print("\n" + "="*50)
    print("🤖 ZEROCLAW TELEGRAM BOT (Упрощенная версия)")
    print("="*50)
    print(f"Токен: {TOKEN[:10]}...")
    print(f"Пользователь ID: 480568670")
    print("\n🚀 Запускаю бота...")
    print("📱 Отправьте /start в Telegram")
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