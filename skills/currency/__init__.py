"""
Currency Skill для ZeroClaw
"""

from .currency_simple import currency


def get_currency_rates(country="KZ", base_currency=None):
    """
    Получает курсы валют для указанной страны
    
    Args:
        country: "KZ" (Казахстан) или "RU" (Россия)
        base_currency: базовая валюта (опционально)
    
    Returns:
        Dict с данными о курсах
    """
    country = country.upper()
    
    if country == "KZ":
        data = currency.get_kz_rates()
    elif country == "RU":
        data = currency.get_ru_rates()
    else:
        raise ValueError(f"Страна {country} не поддерживается. Используйте 'KZ' или 'RU'.")
    
    return data


def convert_currency(amount, from_currency, to_currency, country="KZ"):
    """
    Конвертирует сумму между валютами
    
    Args:
        amount: сумма для конвертации
        from_currency: исходная валюта (например, "KZT", "USD")
        to_currency: целевая валюта (например, "USD", "EUR")
        country: страна для курсов ("KZ" или "RU")
    
    Returns:
        Dict с результатом конвертации
    """
    return currency.convert(amount, from_currency, to_currency, country)


def format_currency_response(data, target_currencies=None):
    """
    Форматирует ответ с курсами валют в читаемый вид
    
    Args:
        data: данные от get_currency_rates()
        target_currencies: список валют для отображения (опционально)
    
    Returns:
        Отформатированная строка
    """
    return currency.format_rates(data)


# Экспортируем основные функции
__all__ = [
    'currency',
    'get_currency_rates',
    'convert_currency',
    'format_currency_response'
]