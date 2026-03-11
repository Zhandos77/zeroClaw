#!/usr/bin/env python3
"""
Тестирование Currency Skill
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency import currency_skill

def test_kazakhstan():
    print("🔍 Тестирование для Казахстана (НБ РК)")
    print("-" * 50)
    
    response = currency_skill.get_rates("KZ")
    
    print(f"Дата: {response.date}")
    print(f"Страна: {response.country}")
    print(f"Источник: {response.source}")
    print(f"Курсов валют: {len(response.rates)}")
    print()
    
    # Форматированный вывод
    formatted = currency_skill.format_response(response)
    print(formatted)
    
    # Конвертация
    print("\n💱 Конвертация:")
    try:
        conv1 = currency_skill.convert(1000, "KZT", "USD", "KZ")
        print(f"1000 KZT → {conv1['converted']:.2f} USD (курс: {conv1['rate']:.2f})")
        
        conv2 = currency_skill.convert(100, "USD", "KZT", "KZ")
        print(f"100 USD → {conv2['converted']:.2f} KZT (курс: {conv2['rate']:.2f})")
        
        conv3 = currency_skill.convert(100, "USD", "EUR", "KZ")
        print(f"100 USD → {conv3['converted']:.2f} EUR (курс: {conv3['rate']:.4f})")
    except Exception as e:
        print(f"Ошибка конвертации: {e}")

def test_russia():
    print("\n🔍 Тестирование для России (ЦБ РФ)")
    print("-" * 50)
    
    response = currency_skill.get_rates("RU")
    
    print(f"Дата: {response.date}")
    print(f"Страна: {response.country}")
    print(f"Источник: {response.source}")
    print(f"Курсов валют: {len(response.rates)}")
    print()
    
    formatted = currency_skill.format_response(response)
    print(formatted)
    
    # Конвертация
    print("\n💱 Конвертация:")
    try:
        conv1 = currency_skill.convert(1000, "RUB", "USD", "RU")
        print(f"1000 RUB → {conv1['converted']:.2f} USD (курс: {conv1['rate']:.2f})")
        
        conv2 = currency_skill.convert(100, "USD", "RUB", "RU")
        print(f"100 USD → {conv2['converted']:.2f} RUB (курс: {conv2['rate']:.2f})")
    except Exception as e:
        print(f"Ошибка конвертации: {e}")

def test_cache():
    print("\n🔍 Тестирование кэширования")
    print("-" * 50)
    
    # Первый запрос
    print("Первый запрос...")
    start_time = time.time()
    response1 = currency_skill.get_rates("KZ")
    time1 = time.time() - start_time
    print(f"Время выполнения: {time1:.3f} сек")
    
    # Второй запрос (должен быть из кэша)
    print("Второй запрос (должен быть из кэша)...")
    start_time = time.time()
    response2 = currency_skill.get_rates("KZ")
    time2 = time.time() - start_time
    print(f"Время выполнения: {time2:.3f} сек")
    
    if time2 < time1 * 0.5:  # Если второй запрос значительно быстрее
        print("✅ Кэширование работает")
    else:
        print("⚠️  Кэширование может не работать оптимально")

if __name__ == "__main__":
    import time
    
    print("🧪 Тестирование Currency Skill")
    print("=" * 60)
    
    test_kazakhstan()
    test_russia()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")
    
    # Пример использования из командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == "kz":
            response = currency_skill.get_rates("KZ")
            print(currency_skill.format_response(response))
        elif sys.argv[1] == "ru":
            response = currency_skill.get_rates("RU")
            print(currency_skill.format_response(response))
        elif sys.argv[1] == "convert" and len(sys.argv) == 5:
            amount = float(sys.argv[2])
            from_curr = sys.argv[3]
            to_curr = sys.argv[4]
            try:
                result = currency_skill.convert(amount, from_curr, to_curr, "KZ")
                print(f"{result['amount']} {result['from']} = {result['converted']} {result['to']}")
            except Exception as e:
                print(f"Ошибка: {e}")