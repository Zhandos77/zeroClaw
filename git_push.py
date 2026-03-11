#!/usr/bin/env python3
import subprocess
import os
import sys

def run_command(cmd, cwd=None):
    """Безопасный запуск команды"""
    print(f"▶️  Выполняю: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        print(f"📤 STDOUT: {result.stdout}")
        if result.stderr:
            print(f"📥 STDERR: {result.stderr}")
        print(f"✅ Код возврата: {result.returncode}")
        return result
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def main():
    print("🚀 Запускаем push в GitHub...")
    
    workspace = "/root/.zeroclaw/workspace"
    
    # 1. Проверяем SSH подключение
    print("\n1. Проверяем SSH подключение к GitHub...")
    ssh_check = run_command("ssh -T git@github.com")
    
    # 2. Переходим в директорию
    os.chdir(workspace)
    print(f"\n2. Текущая директория: {os.getcwd()}")
    
    # 3. Добавляем файлы
    print("\n3. Добавляем файлы в Git...")
    run_command("git add .")
    
    # 4. Создаём коммит
    print("\n4. Создаём коммит...")
    run_command('git commit -m "Initial commit: ZeroClaw configuration"')
    
    # 5. Делаем push
    print("\n5. Делаем push в GitHub...")
    push_result = run_command("git push origin master")
    
    # 6. Проверяем статус
    print("\n6. Проверяем статус...")
    run_command("git status")
    
    print("\n🎉 Готово!")

if __name__ == "__main__":
    main()