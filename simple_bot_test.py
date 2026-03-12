#!/usr/bin/env python3
"""
Простой тест Telegram бота
"""

import telebot

# Токен из конфига (строка 256)
TOKEN = "8666*[REDACTED]"

print(f"🔑 Используется токен: {TOKEN[:10]}...")

# Создаем бота
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Привет! Я тестовый бот. Работаю!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"📝 Вы написали: {message.text}")

print("🚀 Запускаю бота...")
print("📱 Отправь /start в Telegram для проверки")
print("🛑 Ctrl+C для остановки")

try:
    bot.polling(none_stop=True)
except KeyboardInterrupt:
    print("\n👋 Остановка бота...")
except Exception as e:
    print(f"❌ Ошибка: {e}")