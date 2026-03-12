# Команды HealthCheck Skill

## Основные команды

### `/healthcheck` или `/hc`
Полная проверка всех сервисов.

**Пример:**
```
/hc
```

### `/healthcheck [сервис]`
Проверка конкретного сервиса:
- `/healthcheck currency` — проверка источников валют
- `/healthcheck tts` — проверка TTS
- `/healthcheck web` — проверка веб-доступности
- `/healthcheck all` — проверка всего (по умолчанию)

**Примеры:**
```
/healthcheck currency
/hc tts
```

## Сокращённые команды
- `/hc` — алиас для `/healthcheck`
- `/status` — алиас для `/healthcheck`

## Формат ответа

Ответ включает:
1. **Общий статус** (✅ здоров, ⚠️ деградировал, ❌ нездоров)
2. **Время проверки**
3. **Детали по каждому сервису**
4. **Рекомендации** при наличии проблем

## Пример вывода

```
ZeroClaw Health Check
Время: 2026-03-12T10:30:00Z
Общий статус: ✅ HEALTHY
Время проверки: 1250 мс

✅ CURRENCY (450 мс)
  ✅ nbrk_kz (320 мс)
  ✅ yandex_finance (450 мс)
  ❌ openexchangerates (timeout)

✅ TTS (1200 мс)
  📢 edge-tts доступен, голос ru-RU-SvetlanaNeural найден
  ✅ Генерация речи (850 мс)

✅ WEB (320 мс)
  ✅ google (150 мс)
  ✅ yandex (320 мс)
  ✅ github (280 мс)
  ✅ python_org (310 мс)

Рекомендации:
• Open Exchange Rates недоступен. Используйте альтернативные источники.
```

## Интеграция с другими навыками

Другие навыки могут использовать HealthCheck для проверки своих зависимостей:

```python
from skills.healthcheck import check_currency

# Проверка перед использованием currency skill
status = check_currency()
if status["status"] == "healthy":
    # Использовать currency API
    pass
else:
    # Использовать кэшированные данные или альтернативу
    pass
```

## Планирование регулярных проверок

Для автоматической проверки можно создать cron задачу:

```bash
# Каждый час проверять здоровье
cron_add --schedule "0 * * * *" --command "python -m skills.healthcheck.healthcheck --json >> /var/log/zeroclaw_health.log"
```

Или через ZeroClaw API:

```python
from skills.healthcheck import check_all
import json

# Регулярная проверка и логирование
status = check_all()
with open("/var/log/zeroclaw_health.log", "a") as f:
    f.write(json.dumps(status) + "\n")
```

## Тестирование

```bash
# Тестирование из командной строки
cd /root/.zeroclaw/workspace/skills/healthcheck
python healthcheck.py --test-currency
python healthcheck.py --test-tts
python healthcheck.py --test-web
python healthcheck.py --json  # Полная проверка в JSON
```