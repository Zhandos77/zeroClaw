#!/usr/bin/env python3
"""
Демонстрация работы Currency Skill в чате
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_simple import currency


def demo_chat():
    """Демонстрация работы в режиме чата"""
    print("💬 Демо-чат с Currency Skill")
    print("=" * 60)
    print("Доступные команды:")
    print("  /kz          - курсы для Казахстана")
    print("  /ru          - курсы для России")
    print("  /convert     - конвертация валют")
    print("  /help        - помощь")
    print("  /exit        - выход")
    print("=" * 60)
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == "/exit" or command == "exit":
                print("👋 До свидания!")
                break
            
            elif command == "/help" or command == "help":
                print("📋 Доступные команды:")
                print("  /kz          - курсы для Казахстана")
                print("  /ru          - курсы для России")
                print("  /convert     - конвертация валют")
                print("  /help        - помощь")
                print("  /exit        - выход")
                print("\nПримеры:")
                print("  /convert 1000 KZT USD")
                print("  /convert 100 USD KZT")
                print("  /convert 1000 RUB USD ru")
            
            elif command == "/kz" or command == "kz":
                print("\n" + currency.format_rates(currency.get_kz_rates()))
            
            elif command == "/ru" or command == "ru":
                print("\n" + currency.format_rates(currency.get_ru_rates()))
            
            elif command.startswith("/convert"):
                parts = command.split()
                if len(parts) >= 4:
                    try:
                        amount = float(parts[1])
                        from_curr = parts[2].upper()
                        to_curr = parts[3].upper()
                        
                        # Определяем страну
                        country = "KZ"
                        if len(parts) >= 5:
                            country_arg = parts[4].upper()
                            if country_arg in ["KZ", "RU"]:
                                country = country_arg
                        
                        result = currency.convert(amount, from_curr, to_curr, country)
                        
                        print(f"\n💱 Конвертация:")
                        print(f"{result['amount']} {result['from']} = {result['converted']} {result['to']}")
                        print(f"Курс: 1 {result['to']} = {result['rate']} {result['from']}")
                        print(f"Дата: {result['date']}")
                        print(f"Страна: {result['country']}")
                        
                    except ValueError as e:
                        print(f"❌ Ошибка: {e}")
                        print("Используйте: /convert <сумма> <из> <в> [страна]")
                        print("Пример: /convert 1000 KZT USD")
                else:
                    print("❌ Неверный формат команды")
                    print("Используйте: /convert <сумма> <из> <в> [страна]")
                    print("Пример: /convert 1000 KZT USD")
            
            else:
                print("❌ Неизвестная команда. Введите /help для списка команд.")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")


def quick_demo():
    """Быстрая демонстрация"""
    print("🚀 Быстрая демонстрация Currency Skill")
    print("=" * 60)
    
    # 1. Курсы для Казахстана
    print("\n1. 📊 Курсы для Казахстана:")
    kz_data = currency.get_kz_rates()
    print(currency.format_rates(kz_data))
    
    # 2. Конвертация
    print("\n2. 💱 Примеры конвертации:")
    
    # KZT → USD
    conv1 = currency.convert(1000, "KZT", "USD", "KZ")
    print(f"• {conv1['amount']} {conv1['from']} = {conv1['converted']:.2f} {conv1['to']}")
    
    # USD → KZT
    conv2 = currency.convert(100, "USD", "KZT", "KZ")
    print(f"• {conv2['amount']} {conv2['from']} = {conv2['converted']:.2f} {conv2['to']}")
    
    # USD → EUR
    conv3 = currency.convert(100, "USD", "EUR", "KZ")
    print(f"• {conv3['amount']} {conv3['from']} = {conv3['converted']:.2f} {conv3['to']}")
    
    # 3. Курсы для России
    print("\n3. 📊 Курсы для России:")
    ru_data = currency.get_ru_rates()
    print(currency.format_rates(ru_data))
    
    print("\n" + "=" * 60)
    print("✅ Демонстрация завершена")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        demo_chat()
    else:
        quick_demo()