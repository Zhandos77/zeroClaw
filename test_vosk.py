#!/usr/bin/env python3
import vosk
import json
import sys
import os

print("🔧 Тестирование Vosk...")

# Проверяем наличие модели
model_path = "/root/.zeroclaw/workspace/vosk-model-small-ru-0.22"
if not os.path.exists(model_path):
    print(f"❌ Модель не найдена по пути: {model_path}")
    sys.exit(1)

print(f"✅ Модель найдена: {model_path}")

# Пробуем загрузить модель
try:
    model = vosk.Model(model_path)
    print("✅ Модель загружена успешно!")
    
    # Создаём распознаватель
    rec = vosk.KaldiRecognizer(model, 16000)
    print("✅ Распознаватель создан (частота 16kHz)")
    
    # Простая демонстрация
    print("\n📋 Информация о модели:")
    print(f"   • Размер модели: {model.model_size()}")
    print(f"   • Частота: {model.sample_frequency()} Hz")
    print(f"   • Поддерживаемые языки: Русский, Английский")
    
    print("\n🎯 Vosk готов к работе!")
    print("Для теста нужен аудиофайл в формате WAV, 16kHz, mono")
    
except Exception as e:
    print(f"❌ Ошибка при загрузке модели: {e}")
    sys.exit(1)