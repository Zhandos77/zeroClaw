#!/usr/bin/env python3
"""
Тест обработки голосовых сообщений
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_processor import VoiceProcessor, test_voice_processor

def main():
    print("🧪 Тест обработки голосовых для ZeroClaw")
    print("=" * 50)
    
    # Проверяем наличие модели Vosk
    model_path = "/root/.zeroclaw/workspace/model_vosk_ru"
    
    if os.path.exists(model_path):
        print(f"✅ Модель Vosk найдена: {model_path}")
        print(f"   Размер: {sum(os.path.getsize(os.path.join(dirpath, filename)) 
                               for dirpath, dirnames, filenames in os.walk(model_path) 
                               for filename in filenames) / 1024 / 1024:.1f} MB")
    else:
        print("❌ Модель Vosk не найдена")
        print("\n📥 Как скачать модель:")
        print("1. Перейдите в папку workspace:")
        print("   cd /root/.zeroclaw/workspace")
        print("2. Скачайте модель:")
        print("   wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
        print("3. Разархивируйте:")
        print("   unzip vosk-model-small-ru-0.22.zip")
        print("4. Переименуйте:")
        print("   mv vosk-model-small-ru-0.22 model_vosk_ru")
        return
    
    # Тестируем процессор
    print("\n🔧 Инициализация VoiceProcessor...")
    try:
        processor = VoiceProcessor(model_path)
        print("✅ VoiceProcessor инициализирован")
        
        # Тестовый запуск
        print("\n🧪 Запуск тестового распознавания...")
        test_voice_processor()
        
        print("\n🎯 Готов к работе!")
        print("\n📋 Пример использования:")
        print("""
from voice_processor import VoiceProcessor

# Инициализация
processor = VoiceProcessor()

# Обработка голосового файла
result = processor.process_voice_message("voice_message.ogg")

if result["success"]:
    print(f"📝 Распознанный текст: {result['text']}")
else:
    print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        """)
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        print("\n🔧 Устранение неполадок:")
        print("1. Проверьте установлен ли Vosk: pip3 install vosk")
        print("2. Проверьте Python зависимости")
        print("3. Убедитесь что модель загружена корректно")

if __name__ == "__main__":
    main()