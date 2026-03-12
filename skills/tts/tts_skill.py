#!/usr/bin/env python3
"""
TTS Skill - Text-to-Speech преобразование для ZeroClaw
Использует Google TTS API (gTTS) для генерации речи
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def tts_convert(text: str, lang: str = "ru", slow: bool = False, tld: str = "com") -> Optional[str]:
    """
    Конвертирует текст в речь и сохраняет в MP3 файл
    
    Args:
        text: Текст для озвучивания
        lang: Код языка (ru, en, kk и т.д.)
        slow: Медленная речь (для лучшего качества)
        tld: Домен Google (com, ru и т.д.)
    
    Returns:
        Путь к сохраненному MP3 файлу или None при ошибке
    """
    try:
        # Проверка длины текста
        if len(text) > 1000:
            logger.warning(f"Текст слишком длинный ({len(text)} символов), обрезаю до 1000 символов")
            text = text[:1000]
        
        # Импорт gTTS (может потребовать установки)
        try:
            from gtts import gTTS
        except ImportError:
            logger.error("Библиотека gTTS не установлена. Установите: pip install gtts")
            return None
        
        # Создание временного файла
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        # Генерация речи
        logger.info(f"Генерация речи: {len(text)} символов, язык: {lang}")
        tts = gTTS(text=text, lang=lang, slow=slow, tld=tld)
        tts.save(temp_path)
        
        # Проверка размера файла
        file_size = os.path.getsize(temp_path)
        logger.info(f"Файл создан: {temp_path} ({file_size} байт)")
        
        return temp_path
        
    except Exception as e:
        logger.error(f"Ошибка при конвертации TTS: {e}")
        return None

def tts_send(audio_path: str, chat_id: str = None) -> Tuple[bool, str]:
    """
    Отправляет аудиофайл как голосовое сообщение
    
    Args:
        audio_path: Путь к MP3 файлу
        chat_id: ID чата Telegram (если None, будет использован текущий чат)
    
    Returns:
        (success, message): Успешность отправки и сообщение
    """
    try:
        # Проверка существования файла
        if not os.path.exists(audio_path):
            return False, f"Файл не найден: {audio_path}"
        
        # Проверка размера файла (Telegram ограничение ~50MB)
        file_size = os.path.getsize(audio_path)
        if file_size > 50 * 1024 * 1024:
            return False, f"Файл слишком большой: {file_size} байт"
        
        # В ZeroClaw отправка файлов обрабатывается на уровне системы
        # Здесь просто возвращаем информацию о файле
        return True, f"Аудиофайл готов: {audio_path} ({file_size} байт)"
        
    except Exception as e:
        logger.error(f"Ошибка при отправке TTS: {e}")
        return False, f"Ошибка: {e}"

def tts_cleanup(audio_path: str):
    """
    Удаляет временный аудиофайл
    
    Args:
        audio_path: Путь к файлу для удаления
    """
    try:
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
            logger.info(f"Удален временный файл: {audio_path}")
    except Exception as e:
        logger.warning(f"Не удалось удалить файл {audio_path}: {e}")

def main():
    """Тестовая функция для проверки работы TTS"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python tts_skill.py <текст> [язык]")
        print("Пример: python tts_skill.py 'Привет, мир!' ru")
        sys.exit(1)
    
    text = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "ru"
    
    print(f"Конвертация текста: '{text}' (язык: {lang})")
    
    audio_path = tts_convert(text, lang=lang)
    
    if audio_path:
        print(f"Успешно создан файл: {audio_path}")
        print(f"Размер: {os.path.getsize(audio_path)} байт")
        
        # Очистка временного файла
        tts_cleanup(audio_path)
    else:
        print("Ошибка при конвертации TTS")

if __name__ == "__main__":
    main()