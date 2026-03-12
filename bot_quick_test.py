#!/usr/bin/env python3
"""
Быстрый тест Telegram бота
"""

import telebot
import re
import sys

# Получаем токен
with open("/root/.zeroclaw/config.toml", "r") as f:
    content = f.read()

token = None
for line in content.split('\n'):
    if '8666' in line and 'token' in line:
        match = re.search(r'"([^"]+)"', line)
        if match:
            token = match.group(1)
            break

if not token:
    print("❌ Токен не найден")
    sys.exit(1)

print(f"🔑 Токен: {token[:10]}...")

# Создаем бота
bot = telebot.TeleBot(token)

# Простой обработчик
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "✅ Бот работает! Отправьте /test для проверки")

@bot.message_handler(commands=['test'])
def test_handler(message):
    bot.reply_to(message, "🎯 Тест пройден! Бот активен и готов к работе.")

@bot.message_handler(func=lambda message: True)
def echo_handler(message):
    bot.reply_to(message, f"📝 Получено: {message.text}")

print("🚀 Запускаю бота на 30 секунд для теста...")
print("📱 Отправьте /start в Telegram")

# Запускаем на короткое время
import threading
import time

def run_bot():
    try:
        bot.polling(none_stop=True, timeout=10)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Запускаем в отдельном потоке
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

# Ждем 30 секунд
print("⏱️ Бот работает 30 секунд...")
time.sleep(30)
print("⏹️ Останавливаю бота...")
sys.exit(0)