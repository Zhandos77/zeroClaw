#!/usr/bin/env python3
"""
Проверка настроек Telegram бота
"""

import os
import sys

# Проверяем переменные окружения
print("🔍 Проверка переменных окружения:")
print(f"   TELEGRAM_BOT_TOKEN установлен: {'TELEGRAM_BOT_TOKEN' in os.environ}")

# Пробуем получить токен из разных источников
token = None

# 1. Из переменных окружения
token = os.environ.get('TELEGRAM_BOT_TOKEN')
if token:
    print(f"✅ Токен из переменных окружения: {token[:10]}...")
else:
    print("❌ TELEGRAM_BOT_TOKEN не установлен")
    
    # 2. Читаем из конфига
    try:
        import re
        with open("/root/.zeroclaw/config.toml", "r") as f:
            content = f.read()
            
        # Ищем токен в конфиге
        lines = content.split('\n')
        for line in lines:
            if '8666' in line and 'token' in line:
                # Извлекаем токен из строки
                match = re.search(r'"([^"]+)"', line)
                if match:
                    token = match.group(1)
                    print(f"✅ Токен из конфига: {token[:10]}...")
                    break
                    
        if not token:
            print("❌ Токен не найден в конфиге")
            
    except Exception as e:
        print(f"❌ Ошибка чтения конфига: {e}")

if token:
    print(f"\n🔑 Полный токен (первые 20 символов): {token[:20]}...")
    print(f"📏 Длина токена: {len(token)} символов")
    
    # Проверяем формат токена
    if ':' in token:
        print("✅ Токен содержит двоеточие (правильный формат)")
    else:
        print("⚠️ Токен не содержит двоеточие (возможно неполный)")
        
    # Проверяем, начинается ли с цифр
    if token[:4] == '8666':
        print("✅ Токен начинается с 8666 (вероятно правильный)")
else:
    print("\n❌ Токен не найден. Нужно установить его:")
    print("1. Создайте бота через @BotFather в Telegram")
    print("2. Получите токен (выглядит как: 1234567890:ABCdefGHIjklMnoPQRstuVWXyz)")
    print("3. Установите переменную окружения:")
    print("   export TELEGRAM_BOT_TOKEN='ваш_токен'")
    print("4. Или добавьте в конфиг /root/.zeroclaw/config.toml:")
    print('   bot_token = "ваш_токен"')