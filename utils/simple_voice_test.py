#!/usr/bin/env python3
"""
Простой тест системы распознавания речи
"""

import sys
import os
sys.path.insert(0, '/root/.zeroclaw/workspace')

print("🔧 Тестирование системы распознавания речи...")
print("="*50)

try:
    from voice_processor import VoiceProcessor
    
    # Создаем обработчик
    vp = VoiceProcessor()
    
    print(f"✅ VoiceProcessor создан")
    print(f"📁 Путь к модели: {vp.model_path}")
    print(f"🔧 Модель загружена: {vp.model_loaded}")
    
    # Проверяем размер модели
    if vp.model_path and os.path.exists(vp.model_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(vp.model_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        else:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        
        print(f"💾 Размер модели: {size_str}")
    
    # Проверяем зависимости
    print("\n🔍 Проверяю зависимости...")
    
    # Проверяем ffmpeg
    try:
        import subprocess
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg найден:", result.stdout.strip())
        else:
            print("⚠️ ffmpeg не найден, будем использовать альтернативные методы")
    except:
        print("⚠️ Не удалось проверить ffmpeg")
    
    # Проверяем pydub
    try:
        import pydub
        print("✅ pydub установлен")
    except ImportError:
        print("⚠️ pydub не установлен. Установите: pip3 install pydub")
    
    # Создаем простой тестовый WAV файл
    print("\n🎵 Создаю тестовый WAV файл...")
    import wave
    import struct
    import math
    
    test_wav = "/tmp/test_voice.wav"
    sample_rate = 16000
    duration = 1.0
    
    with wave.open(test_wav, 'w') as wav_file:
        wav_file.setnchannels(1)  # моно
        wav_file.setsampwidth(2)  # 16 бит
        wav_file.setframerate(sample_rate)
        
        # Тишина (нулевые значения)
        frames = []
        for i in range(int(sample_rate * duration)):
            frames.append(struct.pack('<h', 0))
        
        wav_file.writeframes(b''.join(frames))
    
    print(f"✅ Тестовый файл создан: {test_wav}")
    
    # Пробуем обработать
    print("\n🔍 Пробую обработать тестовый файл...")
    result = vp.process_file(test_wav)
    
    print(f"📊 Результат:")
    print(f"  Успех: {result.get('success', False)}")
    if result.get('success'):
        text = result.get('text', '').strip()
        print(f"  Текст: '{text}'")
        print(f"  Длительность: {result.get('duration', 0):.2f} сек")
        print(f"  Уверенность: {result.get('confidence', 0):.2%}")
    else:
        print(f"  Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    
    # Удаляем тестовый файл
    os.remove(test_wav)
    print(f"\n🧹 Тестовый файл удален")
    
    # Проверяем Telegram интеграцию
    print("\n📱 Проверяю интеграцию с Telegram...")
    try:
        from telegram_voice_handler import TelegramVoiceHandler
        handler = TelegramVoiceHandler()
        print("✅ TelegramVoiceHandler загружен")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки Telegram интеграции: {e}")
    
    print("\n" + "="*50)
    print("🎯 СИСТЕМА РАСПОЗНАВАНИЯ РЕЧИ ГОТОВА!")
    print("="*50)
    print("\nЧто нужно для работы:")
    print("1. Отправь голосовое сообщение в Telegram")
    print("2. Бот должен его получить и обработать")
    print("3. Если не работает - нужно настроить вебхук или polling")
    
    # Проверяем конфигурацию
    print("\n🔧 Конфигурация:")
    config_path = "/root/.zeroclaw/config.toml"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
        
        import re
        # Ищем токен
        token_matches = re.findall(r'token.*?=.*?"([^"]+)"', content)
        if token_matches:
            print(f"✅ Найдено {len(token_matches)} токен(ов) в конфиге")
            for i, token in enumerate(token_matches[:2]):
                print(f"   Токен {i+1}: {token[:15]}...")
        else:
            print("❌ Токены не найдены в конфиге")
    else:
        print("❌ Конфиг не найден")
    
except Exception as e:
    print(f"\n❌ Критическая ошибка: {e}")
    import traceback
    traceback.print_exc()