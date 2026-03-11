#!/usr/bin/env python3
"""
Тест интеграции Currency Skill с ZeroClaw
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'skills/currency'))

from currency_simple import currency


def test_zero_claw_commands():
    """Тестирование команд, как они будут работать в ZeroClaw"""
    
    print("🧪 Тест интеграции Currency Skill с ZeroClaw")
    print("=" * 60)
    
    # Имитация команды: currency kz
    print("\n1. Команда: 'currency kz'")
    print("-" * 40)
    kz_data = currency.get_kz_rates()
    response = currency.format_rates(kz_data)
    print(response)
    
    # Имитация команды: currency ru
    print("\n2. Команда: 'currency ru'")
    print("-" * 40)
    ru_data = currency.get_ru_rates()
    response = currency.format_rates(ru_data)
    print(response)
    
    # Имитация команды: currency convert
    print("\n3. Команда: 'currency convert 1000 KZT USD'")
    print("-" * 40)
    try:
        result = currency.convert(1000, "KZT", "USD", "KZ")
        print(f"💱 Конвертация:")
        print(f"{result['amount']} {result['from']} = {result['converted']} {result['to']}")
        print(f"Курс: 1 {result['to']} = {result['rate']} {result['from']}")
        print(f"Дата: {result['date']}")
        print(f"Страна: {result['country']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Имитация команды: currency convert с указанием страны
    print("\n4. Команда: 'currency convert 1000 RUB USD ru'")
    print("-" * 40)
    try:
        result = currency.convert(1000, "RUB", "USD", "RU")
        print(f"💱 Конвертация:")
        print(f"{result['amount']} {result['from']} = {result['converted']} {result['to']}")
        print(f"Курс: 1 {result['to']} = {result['rate']} {result['from']}")
        print(f"Дата: {result['date']}")
        print(f"Страна: {result['country']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Тест сокращённых команд
    print("\n5. Сокращённые команды:")
    print("-" * 40)
    print("Команда '/kz' → то же что 'currency kz'")
    print("Команда '/ru' → то же что 'currency ru'")
    print("Команда '/convert 1000 KZT USD' → то же что 'currency convert 1000 KZT USD'")
    
    # Тест ошибок
    print("\n6. Тест обработки ошибок:")
    print("-" * 40)
    
    # Неподдерживаемая валюта
    print("а) Неподдерживаемая валюта:")
    try:
        result = currency.convert(1000, "XYZ", "USD", "KZ")
        print(f"✅ Успешно (не должно быть)")
    except ValueError as e:
        print(f"✅ Корректная ошибка: {e}")
    
    # Неподдерживаемая страна
    print("\nб) Неподдерживаемая страна:")
    try:
        # В текущей реализации будет использована страна по умолчанию (KZ)
        result = currency.convert(1000, "KZT", "USD", "US")
        print(f"✅ Использована страна по умолчанию: {result['country']}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тест интеграции завершён")


def process_command(command: str) -> str:
    """Обрабатывает команду как это будет делать ZeroClaw"""
    parts = command.strip().lower().split()
    
    if not parts:
        return "❌ Пустая команда"
    
    cmd = parts[0]
    
    if cmd in ["currency", "/kz", "/ru", "/convert"]:
        if cmd.startswith("/"):
            # Сокращённые команды
            if cmd == "/kz":
                return currency.format_rates(currency.get_kz_rates())
            elif cmd == "/ru":
                return currency.format_rates(currency.get_ru_rates())
            elif cmd == "/convert":
                if len(parts) >= 4:
                    try:
                        amount = float(parts[1])
                        from_curr = parts[2].upper()
                        to_curr = parts[3].upper()
                        country = "KZ"
                        if len(parts) >= 5:
                            country = parts[4].upper()
                        
                        result = currency.convert(amount, from_curr, to_curr, country)
                        return (f"💱 Конвертация:\n"
                               f"{result['amount']} {result['from']} = {result['converted']} {result['to']}\n"
                               f"Курс: 1 {result['to']} = {result['rate']} {result['from']}\n"
                               f"Дата: {result['date']} | Страна: {result['country']}")
                    except Exception as e:
                        return f"❌ Ошибка: {e}"
                else:
                    return "❌ Формат: /convert <сумма> <из> <в> [страна]"
        
        elif cmd == "currency" and len(parts) > 1:
            subcmd = parts[1]
            if subcmd == "kz":
                return currency.format_rates(currency.get_kz_rates())
            elif subcmd == "ru":
                return currency.format_rates(currency.get_ru_rates())
            elif subcmd == "convert" and len(parts) >= 5:
                try:
                    amount = float(parts[2])
                    from_curr = parts[3].upper()
                    to_curr = parts[4].upper()
                    country = "KZ"
                    if len(parts) >= 6:
                        country = parts[5].upper()
                    
                    result = currency.convert(amount, from_curr, to_curr, country)
                    return (f"💱 Конвертация:\n"
                           f"{result['amount']} {result['from']} = {result['converted']} {result['to']}\n"
                           f"Курс: 1 {result['to']} = {result['rate']} {result['from']}\n"
                           f"Дата: {result['date']} | Страна: {result['country']}")
                except Exception as e:
                    return f"❌ Ошибка: {e}"
            else:
                return "❌ Неизвестная подкоманда. Используйте: kz, ru, convert"
    
    return "❌ Неизвестная команда. Используйте: currency, /kz, /ru, /convert"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Обработка одной команды
        command = " ".join(sys.argv[1:])
        print(f"Команда: {command}")
        print("-" * 40)
        print(process_command(command))
    else:
        # Полный тест
        test_zero_claw_commands()
        
        # Демонстрация обработки команд
        print("\n🎯 Демонстрация обработки команд:")
        print("=" * 60)
        
        test_commands = [
            "currency kz",
            "/kz",
            "currency ru",
            "/ru",
            "currency convert 1000 KZT USD",
            "/convert 100 USD KZT",
            "currency convert 500 EUR USD kz",
            "/convert 1000 RUB USD ru",
            "invalid command"
        ]
        
        for cmd in test_commands:
            print(f"\n📝 Команда: '{cmd}'")
            print("-" * 40)
            response = process_command(cmd)
            print(response)
        
        print("\n" + "=" * 60)
        print("✅ Демонстрация завершена")