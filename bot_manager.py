#!/usr/bin/env python3
"""
Менеджер для управления Telegram ботом
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

BOT_SCRIPT = "/root/.zeroclaw/workspace/telegram_bot_final.py"
LOG_FILE = "/root/.zeroclaw/workspace/bot.log"
PID_FILE = "/root/.zeroclaw/workspace/bot.pid"

def start_bot():
    """Запуск бота в фоновом режиме"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)  # Проверяем, жив ли процесс
            print(f"❌ Бот уже запущен (PID: {pid})")
            return False
        except OSError:
            print(f"⚠️ Старый PID файл найден, но процесс не существует")
            os.remove(PID_FILE)
    
    print("🚀 Запускаю Telegram бота...")
    
    # Запускаем бота в фоне
    with open(LOG_FILE, 'a') as log:
        proc = subprocess.Popen(
            [sys.executable, BOT_SCRIPT],
            stdout=log,
            stderr=log,
            start_new_session=True
        )
    
    # Сохраняем PID
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    
    print(f"✅ Бот запущен с PID: {proc.pid}")
    print(f"📝 Логи пишутся в: {LOG_FILE}")
    print("📱 Отправьте /start в Telegram для проверки")
    
    return True

def stop_bot():
    """Остановка бота"""
    if not os.path.exists(PID_FILE):
        print("❌ Бот не запущен (PID файл не найден)")
        return False
    
    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    print(f"🛑 Останавливаю бота (PID: {pid})...")
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        
        # Проверяем, остановился ли процесс
        try:
            os.kill(pid, 0)
            print(f"⚠️ Процесс не остановился, отправляю SIGKILL...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)
        except OSError:
            pass
        
        os.remove(PID_FILE)
        print("✅ Бот остановлен")
        return True
        
    except OSError as e:
        print(f"❌ Ошибка остановки: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False

def status_bot():
    """Проверка статуса бота"""
    if not os.path.exists(PID_FILE):
        print("❌ Бот не запущен")
        return False
    
    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    try:
        os.kill(pid, 0)
        print(f"✅ Бот запущен (PID: {pid})")
        
        # Показываем последние логи
        if os.path.exists(LOG_FILE):
            print("\n📝 Последние 10 строк лога:")
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()[-10:]
                for line in lines:
                    print(f"   {line.strip()}")
        
        return True
    except OSError:
        print(f"❌ Бот не запущен (процесс {pid} не существует)")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return False

def restart_bot():
    """Перезапуск бота"""
    print("🔄 Перезапускаю бота...")
    stop_bot()
    time.sleep(2)
    start_bot()

def show_logs(lines=20):
    """Показать логи"""
    if not os.path.exists(LOG_FILE):
        print("❌ Лог файл не найден")
        return
    
    print(f"📝 Последние {lines} строк лога:")
    with open(LOG_FILE, 'r') as f:
        all_lines = f.readlines()
        for line in all_lines[-lines:]:
            print(f"   {line.strip()}")

def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("🤖 Менеджер Telegram бота")
        print("=" * 40)
        print("Использование:")
        print("  python3 bot_manager.py start   - запустить бота")
        print("  python3 bot_manager.py stop    - остановить бота")
        print("  python3 bot_manager.py restart - перезапустить бота")
        print("  python3 bot_manager.py status  - статус бота")
        print("  python3 bot_manager.py logs    - показать логи")
        print("  python3 bot_manager.py logs N  - показать N строк лога")
        print("=" * 40)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_bot()
    elif command == 'stop':
        stop_bot()
    elif command == 'restart':
        restart_bot()
    elif command == 'status':
        status_bot()
    elif command == 'logs':
        if len(sys.argv) > 2:
            try:
                lines = int(sys.argv[2])
                show_logs(lines)
            except ValueError:
                print("❌ Неверное количество строк")
        else:
            show_logs()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()