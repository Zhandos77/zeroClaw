#!/usr/bin/env python3
"""
Обработчик голосовых сообщений для Telegram бота ZeroClaw
"""

import os
import tempfile
import logging
from pathlib import Path
from voice_processor import VoiceProcessor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramVoiceHandler:
    """Обработчик голосовых сообщений Telegram"""
    
    def __init__(self, model_path=None):
        """
        Инициализация обработчика
        
        Args:
            model_path: Путь к модели Vosk
        """
        self.processor = VoiceProcessor(model_path)
        logger.info("TelegramVoiceHandler инициализирован")
        
    def download_voice_message(self, bot, voice_message, download_path):
        """
        Скачать голосовое сообщение из Telegram
        
        Args:
            bot: Объект Telegram бота
            voice_message: Объект голосового сообщения
            download_path: Путь для сохранения
            
        Returns:
            bool: Успешно ли скачано
        """
        try:
            # Получаем информацию о файле
            file_info = bot.get_file(voice_message.file_id)
            
            # Скачиваем файл
            downloaded_file = bot.download_file(file_info.file_path)
            
            # Сохраняем
            with open(download_path, 'wb') as f:
                f.write(downloaded_file)
            
            logger.info(f"Голосовое сообщение скачано: {download_path} ({len(downloaded_file)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка скачивания голосового сообщения: {e}")
            return False
    
    def process_telegram_voice(self, bot, voice_message):
        """
        Полная обработка голосового сообщения из Telegram
        
        Args:
            bot: Объект Telegram бота
            voice_message: Объект голосового сообщения
            
        Returns:
            dict: Результат обработки
        """
        logger.info(f"Начало обработки голосового сообщения (id: {voice_message.file_id})")
        
        # Создаём временную директорию
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Пути для файлов
            ogg_path = tmpdir / "voice.ogg"
            result_path = tmpdir / "result.txt"
            
            # Скачиваем голосовое сообщение
            logger.info("Скачивание голосового сообщения...")
            if not self.download_voice_message(bot, voice_message, ogg_path):
                return {
                    "success": False,
                    "error": "Не удалось скачать голосовое сообщение",
                    "text": None
                }
            
            # Обрабатываем голосовое сообщение
            logger.info("Обработка голосового сообщения...")
            result = self.processor.process_voice_message(
                voice_file_path=ogg_path,
                output_text_path=result_path
            )
            
            if result["success"]:
                logger.info(f"Голосовое сообщение успешно обработано: {len(result['text'])} символов")
            else:
                logger.warning(f"Ошибка обработки: {result.get('error')}")
            
            return result
    
    def format_response(self, result, max_length=4000):
        """
        Форматирование ответа для Telegram
        
        Args:
            result: Результат обработки
            max_length: Максимальная длина сообщения Telegram
            
        Returns:
            str: Отформатированный ответ
        """
        if not result["success"]:
            error = result.get("error", "Неизвестная ошибка")
            return f"❌ Не удалось расшифровать голосовое сообщение.\nОшибка: {error}"
        
        text = result["text"]
        
        # Обрезаем если слишком длинное
        if len(text) > max_length:
            text = text[:max_length - 100] + "\n\n... (сообщение обрезано, слишком длинное)"
        
        # Форматируем ответ
        response = f"📝 **Расшифровка голосового сообщения:**\n\n"
        response += f"{text}\n\n"
        response += f"---\n"
        response += f"ℹ️ _Распознано с помощью Vosk (модель: {result.get('model', 'unknown')})_"
        
        return response
    
    def handle_voice_message(self, bot, message):
        """
        Обработчик для Telegram бота
        
        Args:
            bot: Объект Telegram бота
            message: Сообщение с голосовым
            
        Returns:
            str: Ответное сообщение
        """
        logger.info(f"Получено голосовое сообщение от пользователя {message.from_user.id}")
        
        # Отправляем статус обработки
        status_msg = bot.reply_to(message, "🎤 Обрабатываю голосовое сообщение...")
        
        try:
            # Обрабатываем голосовое сообщение
            result = self.process_telegram_voice(bot, message.voice)
            
            # Форматируем ответ
            response = self.format_response(result)
            
            # Удаляем статус сообщение
            try:
                bot.delete_message(message.chat.id, status_msg.message_id)
            except:
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка обработки голосового сообщения: {e}")
            
            # Удаляем статус сообщение
            try:
                bot.delete_message(message.chat.id, status_msg.message_id)
            except:
                pass
            
            return f"❌ Произошла ошибка при обработке голосового сообщения: {str(e)}"


# Пример использования с pyTelegramBotAPI
def create_telegram_bot(token, voice_handler=None):
    """
    Создание Telegram бота с обработкой голосовых
    
    Args:
        token: Токен Telegram бота
        voice_handler: Обработчик голосовых (опционально)
        
    Returns:
        bot: Объект Telegram бота
    """
    try:
        import telebot
        
        # Создаём бота
        bot = telebot.TeleBot(token)
        
        # Создаём обработчик если не передан
        if voice_handler is None:
            voice_handler = TelegramVoiceHandler()
        
        # Обработчик голосовых сообщений
        @bot.message_handler(content_types=['voice'])
        def handle_voice(message):
            response = voice_handler.handle_voice_message(bot, message)
            bot.reply_to(message, response, parse_mode='Markdown')
        
        # Команда /stt (информация)
        @bot.message_handler(commands=['stt', 'voice'])
        def handle_stt_command(message):
            help_text = """
🎤 **Обработка голосовых сообщений**

Я могу расшифровывать голосовые сообщения на русском языке.

**Как использовать:**
1. Просто отправьте мне голосовое сообщение
2. Я автоматически его расшифрую
3. Отправлю текст обратно

**Техническая информация:**
- Используется Vosk (оффлайн распознавание)
- Русская модель small-ru-0.22
- Поддерживаются форматы: OGG, WAV, MP3

**Ограничения:**
- Только русский язык
- Качество зависит от записи
- Длительность до 5 минут

Отправьте голосовое сообщение, чтобы попробовать! 🦀
            """
            bot.reply_to(message, help_text, parse_mode='Markdown')
        
        # Команда /start
        @bot.message_handler(commands=['start'])
        def handle_start(message):
            welcome = """
🦀 **Добро пожаловать в ZeroClaw!**

Я - AI-ассистент с возможностью обработки голосовых сообщений.

**Доступные команды:**
/start - это сообщение
/stt - информация о расшифровке голосовых
/currency - курсы валют
/kz - курсы НБ РК
/ru - курсы ЦБ РФ

**Обработка голосовых:**
Просто отправьте мне голосовое сообщение, и я расшифрую его в текст.

Начните с команды /stt для подробной информации.
            """
            bot.reply_to(message, welcome, parse_mode='Markdown')
        
        logger.info("Telegram бот создан с обработкой голосовых сообщений")
        return bot
        
    except ImportError:
        logger.error("pyTelegramBotAPI не установлен. Установите: pip3 install pyTelegramBotAPI")
        return None


def main():
    """Основная функция для тестирования"""
    print("=" * 60)
    print("🎤 Telegram Voice Handler for ZeroClaw")
    print("=" * 60)
    
    # Проверяем наличие модели
    model_path = "/root/.zeroclaw/workspace/model_vosk_ru"
    
    if not os.path.exists(model_path):
        print(f"❌ Модель Vosk не найдена: {model_path}")
        print("Скачайте: wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip")
        print("Разархивируйте: unzip vosk-model-small-ru-0.22.zip")
        print("Создайте симлинк: ln -s vosk-model-small-ru-0.22 model_vosk_ru")
        return
    
    print(f"✅ Модель Vosk найдена: {model_path}")
    
    # Создаём обработчик
    handler = TelegramVoiceHandler(model_path)
    print("✅ Обработчик создан")
    
    print("\n📋 Интеграция с Telegram ботом:")
    print("""
# 1. Установите pyTelegramBotAPI
pip3 install pyTelegramBotAPI

# 2. Импортируйте обработчик
from telegram_voice_handler import TelegramVoiceHandler, create_telegram_bot

# 3. Создайте обработчик
handler = TelegramVoiceHandler()

# 4. Создайте бота с обработчиком
bot = create_telegram_bot("ВАШ_TELEGRAM_ТОКЕН", handler)

# 5. Запустите бота
bot.polling(none_stop=True)
    """)
    
    print("\n🎯 Готов к работе с голосовыми сообщениями в Telegram!")


if __name__ == "__main__":
    main()