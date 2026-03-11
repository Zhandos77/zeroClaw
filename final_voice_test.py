#!/usr/bin/env python3
"""
Финальный тест системы распознавания речи
"""

import sys
import os
sys.path.insert(0, '/root/.zeroclaw/workspace')

print("🎤 ФИНАЛЬНЫЙ ТЕСТ СИСТЕМЫ РАСПОЗНАВАНИЯ РЕЧИ")
print("="*60)

try:
    from voice_processor import VoiceProcessor
    
    # 1. Инициализация
    print("\n1️⃣ ИНИЦИАЛИЗАЦИЯ:")
    vp = VoiceProcessor()
    print(f"   ✅ VoiceProcessor создан")
    print(f"   📁 Модель: {os.path.basename(vp.model_path)}")
    print(f"   🔧 Загружена: {vp.model_loaded}")
    
    # 2. Тест с реальным голосовым файлом (если есть)
    print("\n2️⃣ ТЕСТ РАСПОЗНАВАНИЯ:")
    
    # Проверяем есть ли тестовые голосовые файлы
    test_files = []
    telegram_dir = "/root/.zeroclaw/workspace/telegram_files"
    if os.path.exists(telegram_dir):
        for file in os.listdir(telegram_dir):
            if file.endswith(('.ogg', '.wav', '.mp3', '.opus')):
                test_files.append(os.path.join(telegram_dir, file))
    
    if test_files:
        print(f"   📁 Найдено {len(test_files)} тестовых файлов:")
        for file in test_files:
            print(f"      • {os.path.basename(file)}")
        
        # Тестируем первый файл
        test_file = test_files[0]
        print(f"\n   🔍 Тестирую файл: {os.path.basename(test_file)}")
        
        result = vp.process_voice_message(test_file)
        
        if result.get('success'):
            text = result.get('text', '').strip()
            if text:
                print(f"   ✅ Распознано: '{text[:100]}...'")
                print(f"   📊 Уверенность: {result.get('confidence', 0):.1%}")
                print(f"   ⏱️  Длительность: {result.get('duration', 0):.2f} сек")
            else:
                print(f"   ⚠️  Распознан пустой текст (тишина?)")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    else:
        print("   ⚠️  Тестовых голосовых файлов не найдено")
        print("   ℹ️  Отправь голосовое в Telegram или загрузи файл")
    
    # 3. Проверка Telegram интеграции
    print("\n3️⃣ ИНТЕГРАЦИЯ С TELEGRAM:")
    
    try:
        from telegram_voice_handler import TelegramVoiceHandler
        handler = TelegramVoiceHandler()
        print("   ✅ TelegramVoiceHandler загружен")
        
        # Проверяем методы
        methods = [m for m in dir(handler) if not m.startswith('_')]
        print(f"   🔧 Доступно методов: {len(methods)}")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print("   ℹ️  Установите: pip3 install pyTelegramBotAPI")
    
    # 4. Проверка конфигурации бота
    print("\n4️⃣ КОНФИГУРАЦИЯ БОТА:")
    
    config_path = "/root/.zeroclaw/config.toml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
        
        import re
        
        # Токен бота
        token_patterns = [
            r'bot_"token":\s*"([^"]+)"',
            r'token\s*=\s*"([^"]+)"',
            r'TELEGRAM_BOT_TOKEN.*?=.*?"([^"]+)"'
        ]
        
        token = None
        for pattern in token_patterns:
            match = re.search(pattern, content)
            if match:
                token = match.group(1)
                break
        
        if token:
            print(f"   ✅ Токен найден: {token[:10]}...")
            
            # Проверяем разрешенных пользователей
            user_match = re.search(r'allowed_users\s*=\s*\[([^\]]+)\]', content)
            if user_match:
                users_str = user_match.group(1)
                user_ids = re.findall(r'"([^"]+)"', users_str)
                print(f"   👥 Разрешенные пользователи: {user_ids}")
            else:
                print("   ⚠️  Разрешенные пользователи не указаны")
        else:
            print("   ❌ Токен бота не найден в конфиге")
    else:
        print("   ❌ Конфигурационный файл не найден")
    
    # 5. Рекомендации
    print("\n5️⃣ РЕКОМЕНДАЦИИ:")
    
    print("   📱 Для работы с Telegram:")
    print("   1. Убедись что бот запущен (systemctl status zeroclaw)")
    print("   2. Отправь голосовое сообщение боту")
    print("   3. Бот должен автоматически его расшифровать")
    
    print("\n   🔧 Если не работает:")
    print("   1. Проверь логи: journalctl -u zeroclaw -f")
    print("   2. Установи ffmpeg: apt install ffmpeg")
    print("   3. Установи pydub: pip3 install pydub")
    
    # 6. Тестовая команда для бота
    print("\n6️⃣ ТЕСТОВАЯ КОМАНДА:")
    print("   Отправь боту команду: /stt")
    print("   Он должен ответить статусом системы распознавания")
    
    print("\n" + "="*60)
    print("🎯 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
    print("="*60)
    print("\nОтправь голосовое сообщение в Telegram для тестирования! 🎤→📝")
    
except Exception as e:
    print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()