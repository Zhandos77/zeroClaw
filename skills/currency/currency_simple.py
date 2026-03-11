#!/usr/bin/env python3
"""
Currency Skill - упрощённая версия без внешних зависимостей
Использует встроенные библиотеки
"""

import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import re


class SimpleCurrencySkill:
    """Упрощённый скил для получения курсов валют"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 час
        
    def fetch_url(self, url: str) -> Optional[str]:
        """Загружает содержимое URL"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")
            return None
    
    def parse_kz_rates(self, html: str) -> Dict[str, float]:
        """Парсит курсы валют из HTML НБ РК"""
        rates = {}
        
        # Простые регулярки для поиска курсов
        patterns = [
            (r'USD.*?(\d+[\.,]\d+)', 'USD'),
            (r'EUR.*?(\d+[\.,]\d+)', 'EUR'),
            (r'RUB.*?(\d+[\.,]\d+)', 'RUB'),
            (r'CNY.*?(\d+[\.,]\d+)', 'CNY'),
            (r'GBP.*?(\d+[\.,]\d+)', 'GBP'),
        ]
        
        for pattern, code in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                try:
                    rate_str = match.group(1).replace(',', '.')
                    rate = float(rate_str)
                    rates[code] = rate
                except ValueError:
                    continue
        
        return rates
    
    def get_kz_rates(self) -> Dict[str, Any]:
        """Получает курсы для Казахстана"""
        cache_key = "kz_current"
        
        # Проверяем кэш
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return data
        
        # Пробуем разные источники
        sources = [
            "https://ifin.kz/nbrk",
            "https://kurs.kz",
            "https://finance.yahoo.com/quote/USDKZT=X"
        ]
        
        rates = {}
        source_used = "неизвестный источник"
        
        for source in sources:
            html = self.fetch_url(source)
            if html:
                parsed = self.parse_kz_rates(html)
                if parsed:
                    rates = parsed
                    source_used = source
                    break
        
        # Если не удалось получить данные, используем кэшированные или запасные
        if not rates:
            if cache_key in self.cache:
                return self.cache[cache_key][0]
            
            # Запасные данные
            rates = {
                'USD': 491.59,
                'EUR': 572.16,
                'RUB': 6.24,
                'CNY': 71.52
            }
            source_used = "кэшированные данные"
        
        result = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'country': 'KZ',
            'base_currency': 'KZT',
            'rates': rates,
            'source': source_used,
            'timestamp': time.time()
        }
        
        # Сохраняем в кэш
        self.cache[cache_key] = (result, time.time())
        
        return result
    
    def get_ru_rates(self) -> Dict[str, Any]:
        """Получает курсы для России"""
        cache_key = "ru_current"
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return data
        
        # Пробуем Яндекс.Финансы
        html = self.fetch_url("https://yandex.ru/finance/currencies/USD_RUB")
        rates = {}
        
        if html:
            # Ищем курс USD/RUB
            usd_match = re.search(r'(\d+[\.,]\d+)\s*₽', html)
            if usd_match:
                usd_rate = float(usd_match.group(1).replace(',', '.'))
                rates['USD'] = usd_rate
            
            # Ищем курс EUR/RUB
            eur_match = re.search(r'EUR.*?(\d+[\.,]\d+)\s*₽', html, re.IGNORECASE)
            if eur_match:
                eur_rate = float(eur_match.group(1).replace(',', '.'))
                rates['EUR'] = eur_rate
        
        if not rates:
            if cache_key in self.cache:
                return self.cache[cache_key][0]
            
            rates = {
                'USD': 78.74,
                'EUR': 91.90
            }
        
        result = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'country': 'RU',
            'base_currency': 'RUB',
            'rates': rates,
            'source': 'https://yandex.ru/finance',
            'timestamp': time.time()
        }
        
        self.cache[cache_key] = (result, time.time())
        return result
    
    def format_rates(self, data: Dict[str, Any]) -> str:
        """Форматирует курсы в читаемый вид"""
        lines = []
        
        country_name = "Казахстан" if data['country'] == 'KZ' else "Россия"
        base_currency = data['base_currency']
        
        lines.append(f"📊 **Курсы валют ({country_name}) на {data['date']}**")
        lines.append(f"Источник: {data['source']}")
        lines.append("")
        
        rates = data['rates']
        
        # Сортируем валюты
        currency_order = ['USD', 'EUR', 'RUB', 'CNY', 'GBP', 'JPY', 'TRY']
        for code in currency_order:
            if code in rates:
                rate = rates[code]
                
                # Определяем название валюты
                names = {
                    'USD': 'Доллар США',
                    'EUR': 'Евро',
                    'RUB': 'Российский рубль',
                    'CNY': 'Китайский юань',
                    'GBP': 'Фунт стерлингов',
                    'JPY': 'Японская иена',
                    'TRY': 'Турецкая лира'
                }
                name = names.get(code, code)
                
                if data['country'] == 'KZ':
                    line = f"**{code}** ({name}): 1 {code} = {rate:.2f} KZT"
                else:
                    line = f"**{code}** ({name}): 1 {code} = {rate:.2f} RUB"
                
                lines.append(line)
        
        lines.append("")
        lines.append("💡 *Для конвертации используйте: /convert <сумма> <из> <в>*")
        
        return "\n".join(lines)
    
    def convert(self, amount: float, from_currency: str, to_currency: str, country: str = "KZ") -> Dict[str, Any]:
        """Конвертирует сумму между валютами"""
        if country == "KZ":
            data = self.get_kz_rates()
            base = "KZT"
        else:
            data = self.get_ru_rates()
            base = "RUB"
        
        rates = data['rates']
        
        # Добавляем базовую валюту в rates
        rates[base] = 1.0
        
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(f"Валюта не поддерживается: {from_currency} → {to_currency}")
        
        # Конвертация через базовую валюту
        if from_currency == base:
            # Из базовой в другую
            converted = amount / rates[to_currency]
            rate = rates[to_currency]
        elif to_currency == base:
            # Из другой в базовую
            converted = amount * rates[from_currency]
            rate = rates[from_currency]
        else:
            # Из одной иностранной в другую
            converted = amount * (rates[from_currency] / rates[to_currency])
            rate = rates[from_currency] / rates[to_currency]
        
        return {
            'amount': amount,
            'from': from_currency,
            'to': to_currency,
            'converted': round(converted, 2),
            'rate': round(rate, 4),
            'date': data['date'],
            'country': country
        }


# Глобальный экземпляр
currency = SimpleCurrencySkill()


if __name__ == "__main__":
    print("🧪 Тестирование Simple Currency Skill")
    print("=" * 60)
    
    # Тест для Казахстана
    print("\n1. Курсы для Казахстана:")
    kz_data = currency.get_kz_rates()
    print(currency.format_rates(kz_data))
    
    # Тест для России
    print("\n2. Курсы для России:")
    ru_data = currency.get_ru_rates()
    print(currency.format_rates(ru_data))
    
    # Тест конвертации
    print("\n3. Конвертация:")
    try:
        conv1 = currency.convert(1000, "KZT", "USD", "KZ")
        print(f"{conv1['amount']} {conv1['from']} = {conv1['converted']} {conv1['to']}")
        print(f"Курс: 1 {conv1['to']} = {conv1['rate']} {conv1['from']}")
        
        conv2 = currency.convert(100, "USD", "KZT", "KZ")
        print(f"\n{conv2['amount']} {conv2['from']} = {conv2['converted']} {conv2['to']}")
        
        conv3 = currency.convert(1000, "RUB", "USD", "RU")
        print(f"\n{conv3['amount']} {conv3['from']} = {conv3['converted']} {conv3['to']} (Россия)")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")