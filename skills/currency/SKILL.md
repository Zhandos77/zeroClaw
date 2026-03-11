# Currency Skill

Получает актуальные курсы валют из различных источников.

## Источники данных
- **НБ РК (Казахстан):** https://ifin.kz/nbrk/YYYY-MM-DD
- **ЦБ РФ (Россия):** https://yandex.ru/finance/currencies/USD_RUB
- **Open Exchange Rates:** https://openexchangerates.org/api/latest.json (требуется API ключ)

## Команды

### `get_currency_rates(country="KZ", base_currency="USD")`
Получает курсы валют для указанной страны.

**Параметры:**
- `country`: "KZ" (Казахстан), "RU" (Россия), "US" (международные)
- `base_currency`: базовая валюта (по умолчанию USD)
- `target_currencies`: список целевых валют (опционально)

**Примеры:**
- `get_currency_rates("KZ")` — все курсы НБ РК
- `get_currency_rates("KZ", "USD", ["KZT", "EUR", "RUB"])` — USD к KZT, EUR, RUB

### `convert_currency(amount, from_currency, to_currency)`
Конвертирует сумму между валютами.

### `get_historical_rates(date, country="KZ")`
Получает исторические курсы на указанную дату.

## Формат ответа

```json
{
  "date": "2026-03-11",
  "country": "KZ",
  "base_currency": "USD",
  "rates": {
    "KZT": 491.59,
    "EUR": 0.86,
    "RUB": 78.74
  },
  "changes": {
    "daily": {"KZT": -0.46, "EUR": +0.07, "RUB": -0.52},
    "monthly": {"KZT": +0.06, "EUR": +2.45, "RUB": +1.4}
  },
  "source": "https://ifin.kz/nbrk/2026-03-11"
}
```

## Реализация

### Текущая реализация (упрощённая)
Использует встроенные библиотеки Python (urllib, re) без внешних зависимостей.

**Основные файлы:**
- `currency_simple.py` — основная реализация
- `test_currency.py` — тесты

### Для Казахстана (НБ РК)
Использует веб-скрапинг ifin.kz с помощью регулярных выражений.

### Для России
Использует Яндекс.Финансы с парсингом через регулярные выражения.

### Кэширование
Курсы кэшируются на 1 час для уменьшения количества запросов.

## Команды для ZeroClaw

### Основные команды:
- `currency kz` - курсы для Казахстана
- `currency ru` - курсы для России  
- `currency convert <сумма> <из> <в> [страна]` - конвертация

### Сокращённые команды:
- `/kz` - алиас для `currency kz`
- `/ru` - алиас для `currency ru`
- `/convert <сумма> <из> <в> [страна]` - алиас для конвертации

Подробнее в файле `commands.md`.

## Кэширование
Курсы кэшируются на 1 час для уменьшения количества запросов.

## Обработка ошибок
- Если источник недоступен, возвращает последние кэшированные данные
- Если дата в будущем, возвращает текущие курсы
- Если валюта не найдена, возвращает ошибку с предложением альтернатив

## Интеграция с ZeroClaw

Для использования в ZeroClaw добавьте обработчик команд:

```python
from skills.currency import get_currency_rates, convert_currency, format_currency_response

# Получение курсов
rates = get_currency_rates("KZ")
formatted = format_currency_response(rates)

# Конвертация
result = convert_currency(1000, "KZT", "USD", "KZ")
```

## Тестирование
```bash
# Тест для Казахстана
curl "https://ifin.kz/nbrk/2026-03-11"

# Тест для России  
curl "https://yandex.ru/finance/currencies/USD_RUB"
```