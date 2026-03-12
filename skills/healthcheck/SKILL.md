# HealthCheck Skill

Проверяет доступность всех внешних сервисов и API, которые использует ZeroClaw.

## Команды

### `/healthcheck` или `/hc`
Проверяет все доступные сервисы и возвращает статус.

### `/healthcheck [service]`
Проверяет конкретный сервис:
- `currency` — проверяет источники курсов валют
- `tts` — проверяет edge-tts
- `web` — проверяет веб-доступность
- `all` — проверяет всё (по умолчанию)

## Проверяемые сервисы

### 1. Currency API
- **НБ РК (Казахстан):** https://ifin.kz/nbrk/ (статус 200)
- **ЦБ РФ (Россия):** https://yandex.ru/finance/currencies/USD_RUB (статус 200)

### 2. TTS Service
- **edge-tts:** проверка доступности через `edge-tts --list-voices`
- **Генерация тестового аудио:** короткий тест на синтез

### 3. Web Access
- **Google:** https://www.google.com
- **Yandex:** https://yandex.ru
- **GitHub:** https://github.com

### 4. Internal Services
- **ZeroClaw API:** проверка внутренних эндпоинтов
- **База данных:** если используется
- **Кэш:** проверка работы кэша

## Формат ответа

```json
{
  "timestamp": "2026-03-12T10:30:00Z",
  "overall": "healthy",
  "services": {
    "currency": {
      "status": "healthy",
      "response_time_ms": 450,
      "details": {
        "nbrk_kz": "available",
        "yandex_finance": "available"
      }
    },
    "tts": {
      "status": "healthy",
      "response_time_ms": 1200,
      "details": "edge-tts доступен, голос ru-RU-SvetlanaNeural найден"
    },
    "web": {
      "status": "healthy",
      "response_time_ms": 320,
      "details": {
        "google": "available",
        "yandex": "available",
        "github": "available"
      }
    }
  },
  "recommendations": []
}
```

## Статусы

- **healthy** — сервис работает нормально
- **degraded** — есть проблемы, но работает частично
- **unhealthy** — сервис недоступен
- **unknown** — статус неизвестен

## Реализация

Основной файл: `healthcheck.py` с функциями:
- `check_currency()` — проверка источников валют
- `check_tts()` — проверка TTS
- `check_web()` — проверка веб-доступности
- `check_all()` — проверка всего

## Интеграция с ZeroClaw

Для использования в ZeroClaw:

```python
from skills.healthcheck import check_all, format_healthcheck_response

status = check_all()
formatted = format_healthcheck_response(status)
```

## Тестирование
```bash
# Тест проверки валют
python -m skills.healthcheck.healthcheck --test-currency

# Тест проверки TTS
python -m skills.healthcheck.healthcheck --test-tts

# Полная проверка
python -m skills.healthcheck.healthcheck
```