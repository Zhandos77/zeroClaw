#!/usr/bin/env python3
"""
Простой помощник для получения курсов валют
"""

import re
from datetime import datetime


def parse_kz_rates(html: str):
    """Парсит курсы валют из HTML НБ РК"""
    rates = {}
    changes_daily = {}
    changes_monthly = {}
    
    # Ищем таблицу с курсами
    lines = html.split('\n')
    
    # Паттерны для поиска основных валют
    patterns = [
        (r'Доллар США.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸', 'USD'),
        (r'Евро.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸', 'EUR'),
        (r'Российский рубль.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸', 'RUB'),
        (r'Юань.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸.*?(\d+[\.,]\d+)\s*₸', 'CNY'),
    ]
    
    for pattern, code in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            try:
                rate_str = match.group(1).replace(',', '.')
                change_daily_str = match.group(2).replace(',', '.')
                change_monthly_str = match.group(3).replace(',', '.')
                
                rates[code] = float(rate_str)
                changes_daily[code] = float(change_daily_str)
                changes_monthly[code] = float(change_monthly_str)
            except (ValueError, IndexError) as e:
                print(f"Ошибка парсинга {code}: {e}")
                continue
    
    return rates, changes_daily, changes_monthly


def format_kz_rates(rates, changes_daily, changes_monthly):
    """Форматирует курсы для вывода"""
    if not rates:
        return "Не удалось получить курсы валют"
    
    lines = []
    lines.append("📊 **Официальные курсы НБ РК на 12 марта 2026**")
    lines.append("")
    
    # Основные валюты
    for code in ['USD', 'EUR', 'RUB', 'CNY']:
        if code in rates:
            rate = rates[code]
            change_daily = changes_daily.get(code, 0)
            change_monthly = changes_monthly.get(code, 0)
            
            names = {
                'USD': 'Доллар США',
                'EUR': 'Евро',
                'RUB': 'Российский рубль',
                'CNY': 'Китайский юань'
            }
            
            name = names.get(code, code)
            
            # Определяем знаки изменений
            daily_sign = "📈" if change_daily > 0 else "📉" if change_daily < 0 else "➡️"
            monthly_sign = "📈" if change_monthly > 0 else "📉" if change_monthly < 0 else "➡️"
            
            line = f"**{code}** ({name}): 1 {code} = {rate:.2f} ₸"
            if change_daily != 0:
                line += f" {daily_sign}{abs(change_daily):.2f} ₸ за день"
            if change_monthly != 0:
                line += f" {monthly_sign}{abs(change_monthly):.2f} ₸ за месяц"
            
            lines.append(line)
    
    lines.append("")
    lines.append("💡 *Для конвертации: /convert <сумма> <из> <в>*")
    lines.append("💱 *Пример: /convert 1000 KZT USD*")
    
    return "\n".join(lines)


def convert_currency(amount, from_currency, to_currency, rates):
    """Конвертирует сумму между валютами"""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        return f"{amount} {from_currency} = {amount} {to_currency} (та же валюта)"
    
    # Если конвертируем в тенге
    if from_currency in rates and to_currency == "KZT":
        converted = amount * rates[from_currency]
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
    
    # Если конвертируем из тенге
    if from_currency == "KZT" and to_currency in rates:
        converted = amount / rates[to_currency]
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
    
    # Если конвертируем между иностранными валютами
    if from_currency in rates and to_currency in rates:
        # Сначала в тенге, потом в целевую валюту
        in_kzt = amount * rates[from_currency]
        converted = in_kzt / rates[to_currency]
        return f"{amount} {from_currency} = {converted:.2f} {to_currency}"
    
    return f"Не удалось конвертировать {from_currency} → {to_currency}. Доступные валюты: {', '.join(rates.keys())}"


if __name__ == "__main__":
    # Пример использования
    with open("test_currency.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    rates, daily, monthly = parse_kz_rates(html)
    print(format_kz_rates(rates, daily, monthly))
    
    # Тест конвертации
    print("\n🧪 Тест конвертации:")
    print(convert_currency(1000, "KZT", "USD", rates))
    print(convert_currency(100, "USD", "KZT", rates))
    print(convert_currency(1000, "EUR", "USD", rates))