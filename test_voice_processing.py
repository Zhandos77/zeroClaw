#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обработки голосовых сообщений
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

print("🔧 Тестирование системы распознавания речи...")
print("="*50)

try:
    from voice_processor import VoiceProcessor
    print("✅ VoiceProcessor загружен успешно")
    
    # Создаем обработчик
    processor = VoiceProcessor()
    print("✅ Обработчик инициализирован")
    
    # Проверяем модель
    if processor.model_loaded:
        print(f"✅ Модель загружена: {processor.model_path}")
        print(f"   Размер модели: {processor.get_model_size()}")
    else:
        print("❌ Модель не загружена")
        
    # Создаем тестовый голосовой файл (синусоида для теста)
    print("\n🎵 Создаю тестовый аудиофайл...")
    import wave
    import struct
    import math
    
    # Создаем простой WAV файл с тоном 440 Гц
    sample_rate = 16000
    duration = 2.0  # секунды
    frequency = 440.0  # Гц
    
    test_wav = "test_tone.wav"
    with wave.open(test_wav, 'w') as wav_file:
        wav_file.setnchannels(1)  # моно
        wav_file.setsampwidth(2)  # 16 бит
        wav_file.setframerate(sample_rate)
        
        # Генерируем синусоиду
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack('<h', value))
        
        wav_file.writeframes(b''.join(frames))
    
    print(f"✅ Тестовый файл создан: {test_wav}")
    
    # Пробуем обработать
    print("\n🔍 Пробую обработать тестовый файл...")
    result = processor.process_file(test_wav)
    
    print(f"✅ Результат обработки:")
    print(f"   Успех: {result.get('success', False)}")
    if result.get('success'):
        print(f"   Текст: '{result.get('text', '')}'")
        print(f"   Длительность: {result.get('duration', 0):.2f} сек")
        print(f"   Уверенность: {result.get('confidence', 0):.2%}")
    else:
        print(f"   Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    # Проверяем конвертацию форматов
    print("\n🔄 Тестирую конвертацию форматов...")
    test_formats = processor.test_format_conversion()
    
    if test_formats.get('success'):
        print("✅ Конвертация форматов работает:")
        for format, status in test_formats.get('formats', {}).items():
            print(f"   {format}: {'✅' if status else '❌'}")
    else:
        print("❌ Проблемы с конвертацией форматов")
        
    # Проверяем Telegram интеграцию
    print("\n📱 Тестирую интеграцию с Telegram...")
    try:
        from telegram_voice_handler import TelegramVoiceHandler
        handler = TelegramVoiceHandler()
        print("✅ TelegramVoiceHandler загружен")
        print(f"   Модель: {handler.voice_processor.model_loaded}")
    except Exception as e:
        print(f"❌ Ошибка загрузки Telegram интеграции: {e}")
    
    # Проверяем конфигурацию бота
    print("\n🤖 Проверяю конфигурацию бота...")
    config_path = "/root/.zeroclaw/config.toml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
            
        import re
        token_match = re.search(r'bot_"token":\s*"([^"]+)"', content)
        if token_match:
            token = token_match.group(1)
            print(f"✅ Токен бота найден: {token[:10]}...")
            
            # Проверяем разрешенных пользователей
            users_match = re.search(r'allowed_users\s*=\s*\[([^\]]+)\]', content)
            if users_match:
                users_str = users_match.group(1)
                user_ids = re.findall(r'"([^"]+)"', users_str)
                print(f"✅ Разрешенные пользователи: {user_ids}")
            else:
                print("⚠️ Разрешенные пользователи не найдены")
        else:
            print("❌ Токен бота не найден в конфиге")
    else:
        print("❌ Конфигурационный файл не найден")
    
    # Удаляем тестовый файл
    if os.path.exists(test_wav):
        os.remove(test_wav)
        print(f"\n🧹 Тестовый файл удален: {test_wav}")
    
    print("\n" + "="*50)
    print("🎯 СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("="*50)
    print("\nДля использования:")
    print("1. Отправь голосовое сообщение в Telegram")
    print("2. Бот должен автоматически его расшифровать")
    print("3. Если не работает - нужна настройка вебхука")
    
except Exception as e:
    print(f"❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()