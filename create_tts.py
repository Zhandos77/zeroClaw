#!/usr/bin/env python3
from gtts import gTTS
import os

# Текст для озвучивания
text = "Привет, как дела?"

# Создаем TTS объект
tts = gTTS(text=text, lang='ru')

# Сохраняем в файл
output_file = "hello_voice.mp3"
tts.save(output_file)

# Проверяем результат
if os.path.exists(output_file):
    size = os.path.getsize(output_file)
    print(f"✅ Аудиофайл создан: {output_file}")
    print(f"📏 Размер: {size} байт")
    print(f"📝 Текст: '{text}'")
else:
    print("❌ Ошибка: файл не создан")