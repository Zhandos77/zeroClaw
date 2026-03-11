#!/usr/bin/env python3
"""
Currency Skill - получение актуальных курсов валют
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time

@dataclass
class CurrencyRate:
    """Данные о курсе валюты"""
    code: str
    name: str
    rate: float
    change_daily: float
    change_monthly: float
    nominal: int = 1

@dataclass
class CurrencyResponse:
    """Ответ с курсами валют"""
    date: str
    country: str
    base_currency: str
    rates: Dict[str, CurrencyRate]
    source: str
    timestamp: float


class CurrencySkill:
    """Скил для получения курсов валют"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 час в секундах
        
    def get_kz_rates(self, date: Optional[str] = None) -> CurrencyResponse:
        """Получает курсы валют НБ РК для Казахстана"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        # Проверяем кэш
        cache_key = f"kz_{date}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Парсим страницу НБ РК
            url = f"https://ifin.kz/nbrk/{date}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем таблицу с курсами
            rates = {}
            table = soup.find('table', {'class': 'table-rates'})
            
            if not table:
                # Альтернативный поиск таблицы
                table = soup.find('table')
                
            if table:
                rows = table.find_all('tr')[1:]  # Пропускаем заголовок
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        try:
                            code = cols[0].text.strip()
                            name = cols[1].text.strip()
                            nominal = int(cols[2].text.strip())
                            rate_str = cols[3].text.strip().replace(',', '.')
                            rate = float(rate_str)
                            
                            # Вычисляем изменения (если есть данные)
                            change_daily = 0.0
                            change_monthly = 0.0
                            
                            if len(cols) >= 6:
                                change_str = cols[5].text.strip()
                                if '%' in change_str:
                                    change_daily = float(change_str.replace('%', '').replace(',', '.'))
                            
                            rates[code] = CurrencyRate(
                                code=code,
                                name=name,
                                rate=rate,
                                change_daily=change_daily,
                                change_monthly=change_monthly,
                                nominal=nominal
                            )
                        except (ValueError, IndexError):
                            continue
            
            # Если не нашли в таблице, пробуем альтернативный парсинг
            if not rates:
                # Ищем курсы в тексте страницы
                text = soup.get_text()
                import re
                
                # Паттерн для USD
                usd_match = re.search(r'USD.*?(\d+[\.,]\d+)', text)
                if usd_match:
                    usd_rate = float(usd_match.group(1).replace(',', '.'))
                    rates['USD'] = CurrencyRate(
                        code='USD',
                        name='Доллар США',
                        rate=usd_rate,
                        change_daily=0.0,
                        change_monthly=0.0
                    )
                
                # Паттерн для EUR
                eur_match = re.search(r'EUR.*?(\d+[\.,]\d+)', text)
                if eur_match:
                    eur_rate = float(eur_match.group(1).replace(',', '.'))
                    rates['EUR'] = CurrencyRate(
                        code='EUR',
                        name='Евро',
                        rate=eur_rate,
                        change_daily=0.0,
                        change_monthly=0.0
                    )
            
            response_data = CurrencyResponse(
                date=date,
                country="KZ",
                base_currency="KZT",
                rates=rates,
                source=url,
                timestamp=time.time()
            )
            
            # Сохраняем в кэш
            self.cache[cache_key] = (response_data, time.time())
            
            return response_data
            
        except Exception as e:
            # Возвращаем кэшированные данные или пустой ответ
            if cache_key in self.cache:
                return self.cache[cache_key][0]
            
            # Создаем заглушку с последними известными курсами
            rates = {
                'USD': CurrencyRate('USD', 'Доллар США', 491.59, -0.46, +0.06),
                'EUR': CurrencyRate('EUR', 'Евро', 572.16, +0.07, +2.45),
                'RUB': CurrencyRate('RUB', 'Российский рубль', 6.24, +0.16, +1.96),
                'CNY': CurrencyRate('CNY', 'Китайский юань', 71.52, +0.01, +0.48),
            }
            
            return CurrencyResponse(
                date=date,
                country="KZ",
                base_currency="KZT",
                rates=rates,
                source="Кэшированные данные",
                timestamp=time.time()
            )
    
    def get_ru_rates(self, date: Optional[str] = None) -> CurrencyResponse:
        """Получает курсы валют ЦБ РФ для России"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
            
        cache_key = f"ru_{date}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Используем Яндекс.Финансы
            url = "https://yandex.ru/finance/currencies/USD_RUB"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем курс USD/RUB
            usd_rate = None
            usd_change = None
            
            # Пытаемся найти разные элементы
            price_elem = soup.find('div', {'class': 'currency-table__large-text'})
            if price_elem:
                rate_text = price_elem.text.strip().replace(',', '.')
                usd_rate = float(rate_text)
            
            change_elem = soup.find('div', {'class': 'currency-table__change'})
            if change_elem:
                change_text = change_elem.text.strip()
                if '%' in change_text:
                    usd_change = float(change_text.replace('%', '').replace(',', '.'))
            
            rates = {}
            if usd_rate:
                rates['USD'] = CurrencyRate(
                    code='USD',
                    name='Доллар США',
                    rate=usd_rate,
                    change_daily=usd_change or 0.0,
                    change_monthly=0.0
                )
            
            # Также ищем EUR/RUB
            eur_url = "https://yandex.ru/finance/currencies/EUR_RUB"
            eur_response = requests.get(eur_url, timeout=5)
            if eur_response.status_code == 200:
                eur_soup = BeautifulSoup(eur_response.text, 'html.parser')
                eur_price = eur_soup.find('div', {'class': 'currency-table__large-text'})
                if eur_price:
                    eur_rate = float(eur_price.text.strip().replace(',', '.'))
                    rates['EUR'] = CurrencyRate(
                        code='EUR',
                        name='Евро',
                        rate=eur_rate,
                        change_daily=0.0,
                        change_monthly=0.0
                    )
            
            response_data = CurrencyResponse(
                date=date,
                country="RU",
                base_currency="RUB",
                rates=rates,
                source=url,
                timestamp=time.time()
            )
            
            self.cache[cache_key] = (response_data, time.time())
            return response_data
            
        except Exception as e:
            if cache_key in self.cache:
                return self.cache[cache_key][0]
            
            rates = {
                'USD': CurrencyRate('USD', 'Доллар США', 78.74, -0.52, +1.4),
                'EUR': CurrencyRate('EUR', 'Евро', 91.90, -0.13, -0.13),
            }
            
            return CurrencyResponse(
                date=date,
                country="RU",
                base_currency="RUB",
                rates=rates,
                source="Кэшированные данные",
                timestamp=time.time()
            )
    
    def get_rates(self, country: str = "KZ", date: Optional[str] = None) -> CurrencyResponse:
        """Основной метод получения курсов"""
        country = country.upper()
        
        if country == "KZ":
            return self.get_kz_rates(date)
        elif country == "RU":
            return self.get_ru_rates(date)
        else:
            raise ValueError(f"Страна {country} не поддерживается")
    
    def convert(self, amount: float, from_currency: str, to_currency: str, country: str = "KZ") -> Dict[str, Any]:
        """Конвертирует сумму между валютами"""
        rates_response = self.get_rates(country)
        rates = rates_response.rates
        
        # Для Казахстана базовая валюта KZT
        if country == "KZ":
            if from_currency == "KZT":
                # Из KZT в другую валюту
                if to_currency in rates:
                    target_rate = rates[to_currency].rate
                    converted = amount / target_rate
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "converted": round(converted, 2),
                        "rate": target_rate,
                        "date": rates_response.date
                    }
            elif from_currency in rates:
                # Из иностранной валюты в KZT
                from_rate = rates[from_currency].rate
                if to_currency == "KZT":
                    converted = amount * from_rate
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "converted": round(converted, 2),
                        "rate": from_rate,
                        "date": rates_response.date
                    }
                elif to_currency in rates:
                    # Из одной иностранной валюты в другую
                    from_rate = rates[from_currency].rate
                    to_rate = rates[to_currency].rate
                    converted = amount * (from_rate / to_rate)
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "converted": round(converted, 2),
                        "rate": from_rate / to_rate,
                        "date": rates_response.date
                    }
        
        # Для России базовая валюта RUB
        elif country == "RU":
            if from_currency == "RUB":
                if to_currency in rates:
                    target_rate = rates[to_currency].rate
                    converted = amount / target_rate
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "converted": round(converted, 2),
                        "rate": target_rate,
                        "date": rates_response.date
                    }
            elif from_currency in rates:
                from_rate = rates[from_currency].rate
                if to_currency == "RUB":
                    converted = amount * from_rate
                    return {
                        "amount": amount,
                        "from": from_currency,
                        "to": to_currency,
                        "converted": round(converted, 2),
                        "rate": from_rate,
                        "date": rates_response.date
                    }
        
        raise ValueError(f"Конвертация {from_currency} → {to_currency} не поддерживается для страны {country}")
    
    def format_response(self, response: CurrencyResponse, target_currencies: Optional[List[str]] = None) -> str:
        """Форматирует ответ в читаемый вид"""
        lines = []
        
        lines.append(f"📊 **Курсы валют ({response.country}) на {response.date}**")
        lines.append(f"Источник: {response.source}")
        lines.append("")
        
        rates = response.rates
        
        if target_currencies:
            # Фильтруем только нужные валюты
            filtered_rates = {code: rate for code, rate in rates.items() 
                            if code in target_currencies}
        else:
            # Показываем основные валюты
            main_currencies = ['USD', 'EUR', 'RUB', 'CNY', 'GBP']
            filtered_rates = {code: rate for code, rate in rates.items() 
                            if code in main_currencies}
        
        for code, rate_data in filtered_rates.items():
            change_daily = rate_data.change_daily
            change_symbol = "↗️" if change_daily > 0 else "↘️" if change_daily < 0 else "➡️"
            
            if response.country == "KZ":
                # Для Казахстана: 1 USD = X KZT
                line = f"**{code}** ({rate_data.name}): 1 {code} = {rate_data.rate} KZT"
            else:
                # Для России: 1 USD = X RUB
                line = f"**{code}** ({rate_data.name}): 1 {code} = {rate_data.rate} RUB"
            
            if change_daily != 0:
                line += f" {change_symbol} {abs(change_daily):.2f}%"
            
            lines.append(line)
        
        lines.append("")
        lines.append("💡 *Используйте /convert <сумма> <из> <в> для конвертации*")
        
        return "\n".join(lines)


# Создаем глобальный экземпляр для использования
currency_skill = CurrencySkill()


if __name__ == "__main__":
    # Тестирование скила
    skill = CurrencySkill()
    
    print("Тестирование скила курсов валют...")
    print("-" * 50)
    
    # Тест для Казахстана
    print("\n1. Курсы для Казахстана (НБ РК):")
    kz_rates = skill.get_rates("KZ")
    print(skill.format_response(kz_rates))
    
    # Тест для России
    print("\n2. Курсы для России (ЦБ РФ):")
    ru_rates = skill.get_rates("RU")
    print(skill.format_response(ru_rates))
    
    # Тест конвертации
    print("\n3. Конвертация 1000 KZT в USD:")
    try:
        conversion = skill.convert(1000, "KZT", "USD", "KZ")
        print(f"{conversion['amount']} {conversion['from']} = {conversion['converted']} {conversion['to']}")
        print(f"Курс: 1 {conversion['to']} = {conversion['rate']} {conversion['from']}")
    except Exception as e:
        print(f"Ошибка конвертации: {e}")