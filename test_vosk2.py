#!/usr/bin/env python3
import vosk
import json
import sys
import os

# Перенаправляем stderr в лог-файл
import sys
sys.stderr = open('/tmp/vosk_test.log', 'w')

print("🔧 Тестирование Vosk...")

model_path = "/root/.zeroclaw/workspace/vosk-model-small-ru-0.22"

if not os.path.exists(model_path):
    print(f"❌ Модель не найдена")
    sys.exit(1)

try:
    print("🔄 Загрузка модели...")
    model = vosk.Model(model_path)
    print("✅ Модель загружена!")
    
    rec = vosk.KaldiRecognizer(model, 16000)
    print(f"✅ Распознаватель создан")
    
    # Тестовые данные (пустые - просто проверка)
    test_audio = b'\x00' * 3200  # 0.1 секунда тишины (16kHz * 0.1 * 2 bytes)
    
    if rec.AcceptWaveform(test_audio):
        result = json.loads(rec.Result())
        print(f"📝 Результат: {result.get('text', 'пусто')}")
    else:
        print("📝 Частичный результат получен")
        
    print("\n🎯 Vosk установлен и работает!")
    print("Модель: vosk-model-small-ru-0.22 (русская, 40MB)")
    print("Готов к расшифровке голосовых сообщений!")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()