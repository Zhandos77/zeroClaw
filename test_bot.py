#!/usr/bin/env python3
"""
Тестовый Telegram бот для проверки обработки голосовых
"""

import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_bot_setup():
    """Тест настройки бота"""
    print("🧪 Тест настройки Telegram бота")
    print("=" * 50)
    
    # Проверяем зависимости
    print("🔍 Проверка зависимостей...")
    
    try:
        import telebot
        print("✅ pyTelegramBotAPI установлен")
    except ImportError:
        print("❌ pyTelegramBotAPI не установлен")
        print("   Установите: pip3 install pyTelegramBotAPI")
        return False
    
    try:
        import vosk
        print("✅ Vosk установлен")
    except ImportError:
        print("❌ Vosk не установлен")
        print("   Установите: pip3 install vosk")
        return False
    
    # Проверяем модель
    model_path = "/root/.zeroclaw/workspace/model_vosk_ru"
    if os.path.exists(model_path):
        print(f"✅ Модель Vosk найдена: {model_path}")
    else:
        print(f"❌ Модель Vosk не найдена: {model_path}")
        return False
    
    # Проверяем наши модули
    print("\n🔧 Проверка наших модулей...")
    try:
        from voice_processor import VoiceProcessor
        print("✅ VoiceProcessor импортируется")
        
        from telegram_voice_handler import TelegramVoiceHandler
        print("✅ TelegramVoiceHandler импортируется")
        
        # Тест создания обработчика
        handler = TelegramVoiceHandler(model_path)
        print("✅ Обработчик создан успешно")
        
    except Exception as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Все проверки пройдены!")
    return True

def create_minimal_bot():
    """Создание минимального тестового бота"""
    print("\n🤖 Создание тестового бота...")
    
    # Импортируем здесь, чтобы не падать раньше времени
    try:
        import telebot
        from telegram_voice_handler import create_telegram_bot
        
        # Проверяем наличие токена
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            print("⚠️ TELEGRAM_BOT_TOKEN не установлен в переменных окружения")
            print("\n📋 Как настроить бота:")
            print("1. Создайте бота через @BotFather")
            print("2. Получите токен")
            print("3. Установите переменную окружения:")
            print("   export TELEGRAM_BOT_TOKEN='ваш_токен'")
            print("4. Запустите бота:")
            print("   python3 test_bot.py --run")
            return None
        
        # Создаём бота
        print(f"🔑 Используется токен: {token[:10]}...")
        bot = create_telegram_bot(token)
        
        if bot:
            print("✅ Бот создан успешно")
            return bot
        else:
            print("❌ Не удалось создать бота")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Основная функция"""
    print("🎤 Тест обработки голосовых для ZeroClaw Telegram бота")
    print("=" * 60)
    
    # Проверяем аргументы
    run_bot = "--run" in sys.argv
    
    # Выполняем проверки
    if not test_bot_setup():
        print("\n❌ Настройка не пройдена, исправьте ошибки выше")
        return
    
    print("\n" + "=" * 60)
    print("✅ Система готова к обработке голосовых сообщений!")
    print("=" * 60)
    
    if run_bot:
        print("\n🚀 Запуск бота...")
        bot = create_minimal_bot()
        if bot:
            print("\n🤖 Бот запущен. Ожидаю сообщений...")
            print("📱 Отправьте голосовое сообщение в Telegram для теста")
            print("📝 Или команду /stt для информации")
            print("\n🛑 Для остановки нажмите Ctrl+C")
            
            try:
                bot.polling(none_stop=True)
            except KeyboardInterrupt:
                print("\n👋 Остановка бота...")
            except Exception as e:
                print(f"❌ Ошибка при работе бота: {e}")
    else:
        print("\n📋 Для запуска бота выполните:")
        print("   python3 test_bot.py --run")
        print("\n⚠️ Предварительно установите переменную окружения:")
        print("   export TELEGRAM_BOT_TOKEN='ваш_токен'")
        
        print("\n🧪 Для теста обработки голосовых без бота:")
        print("""
# Создайте тестовый OGG файл или используйте существующий
from voice_processor import VoiceProcessor

processor = VoiceProcessor()
result = processor.process_voice_message("тестовый_файл.ogg")

if result["success"]:
    print(f"Распознанный текст: {result['text']}")
else:
    print(f"Ошибка: {result.get('error')}")
        """)

if __name__ == "__main__":
    main()