#!/usr/bin/env python3
"""
HealthCheck Skill для ZeroClaw
Проверяет доступность внешних сервисов и API
"""

import time
import subprocess
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import urllib.request
import urllib.error

def check_url(url: str, timeout: int = 10) -> Tuple[bool, int, Optional[str]]:
    """
    Проверяет доступность URL
    
    Возвращает: (доступен, время_ответа_мс, сообщение_об_ошибке)
    """
    start_time = time.time()
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (ZeroClaw HealthCheck)'
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return True, elapsed_ms, None
    except urllib.error.HTTPError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        # HTTP ошибки (404, 500 и т.д.) - сервис доступен, но с ошибкой
        return False, elapsed_ms, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return False, elapsed_ms, str(e.reason)
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return False, elapsed_ms, str(e)

def check_currency() -> Dict:
    """
    Проверяет источники курсов валют
    """
    services = {
        "nbrk_kz": "https://ifin.kz/nbrk/",
        "yandex_finance": "https://yandex.ru/finance/currencies/USD_RUB"
    }
    
    results = {}
    total_healthy = 0
    total_checks = 0
    max_response_time = 0
    
    for name, url in services.items():
        total_checks += 1
        available, response_time, error = check_url(url, timeout=15)
        
        if available:
            total_healthy += 1
            status = "healthy"
        else:
            status = "unhealthy"
        
        results[name] = {
            "status": status,
            "available": available,
            "response_time_ms": response_time,
            "url": url,
            "error": error
        }
        
        max_response_time = max(max_response_time, response_time)
    
    # Определяем общий статус
    if total_healthy == total_checks:
        overall_status = "healthy"
    elif total_healthy >= total_checks / 2:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "response_time_ms": max_response_time,
        "details": results,
        "healthy_services": total_healthy,
        "total_services": total_checks
    }

def check_tts() -> Dict:
    """
    Проверяет доступность edge-tts
    """
    start_time = time.time()
    
    try:
        # Проверяем, установлен ли edge-tts
        result = subprocess.run(
            ["edge-tts", "--list-voices"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        if result.returncode == 0:
            # Проверяем наличие русского голоса
            if "ru-RU-SvetlanaNeural" in result.stdout:
                status = "healthy"
                details = "edge-tts доступен, голос ru-RU-SvetlanaNeural найден"
            else:
                status = "degraded"
                details = "edge-tts доступен, но русский голос не найден"
        else:
            status = "unhealthy"
            details = f"edge-tts ошибка: {result.stderr[:100]}"
        
        # Тестовая генерация (короткая)
        test_start = time.time()
        test_result = subprocess.run(
            ["edge-tts", "--voice", "ru-RU-SvetlanaNeural", "--text", "Тест", "--write-media", "/tmp/test_tts.mp3"],
            capture_output=True,
            text=True,
            timeout=10
        )
        test_time = int((time.time() - test_start) * 1000)
        
        if test_result.returncode == 0:
            generation_status = "healthy"
        else:
            generation_status = "unhealthy"
            status = "unhealthy"  # Обновляем основной статус
        
        return {
            "status": status,
            "response_time_ms": elapsed_ms,
            "details": details,
            "generation": {
                "status": generation_status,
                "response_time_ms": test_time,
                "error": test_result.stderr[:100] if test_result.returncode != 0 else None
            },
            "voices_available": "ru-RU-SvetlanaNeural" in result.stdout if result.returncode == 0 else False
        }
        
    except FileNotFoundError:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "unhealthy",
            "response_time_ms": elapsed_ms,
            "details": "edge-tts не установлен",
            "generation": {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": "edge-tts не найден"
            },
            "voices_available": False
        }
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "unhealthy",
            "response_time_ms": elapsed_ms,
            "details": "edge-tts timeout при проверке голосов",
            "generation": {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": "timeout"
            },
            "voices_available": False
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "unhealthy",
            "response_time_ms": elapsed_ms,
            "details": f"Ошибка при проверке TTS: {str(e)}",
            "generation": {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": str(e)
            },
            "voices_available": False
        }

def check_web() -> Dict:
    """
    Проверяет общую веб-доступность
    """
    services = {
        "google": "https://www.google.com",
        "yandex": "https://yandex.ru",
        "github": "https://github.com",
        "python_org": "https://www.python.org"
    }
    
    results = {}
    total_healthy = 0
    total_checks = 0
    max_response_time = 0
    
    for name, url in services.items():
        total_checks += 1
        available, response_time, error = check_url(url, timeout=10)
        
        if available:
            total_healthy += 1
            status = "healthy"
        else:
            status = "unhealthy"
        
        results[name] = {
            "status": status,
            "available": available,
            "response_time_ms": response_time,
            "url": url,
            "error": error
        }
        
        max_response_time = max(max_response_time, response_time)
    
    # Определяем общий статус
    if total_healthy == total_checks:
        overall_status = "healthy"
    elif total_healthy >= total_checks / 2:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "response_time_ms": max_response_time,
        "details": results,
        "healthy_services": total_healthy,
        "total_services": total_checks
    }

def check_all() -> Dict:
    """
    Проверяет все сервисы
    """
    start_time = time.time()
    
    results = {
        "currency": check_currency(),
        "tts": check_tts(),
        "web": check_web()
    }
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    # Определяем общий статус
    statuses = [service["status"] for service in results.values()]
    
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "overall": overall_status,
        "response_time_ms": elapsed_ms,
        "services": results
    }

def format_healthcheck_response(data: Dict) -> str:
    """
    Форматирует результат проверки в читаемый текст
    """
    timestamp = data.get("timestamp", "")
    overall = data.get("overall", "unknown")
    response_time = data.get("response_time_ms", 0)
    
    # Эмодзи для статусов
    status_emojis = {
        "healthy": "✅",
        "degraded": "⚠️",
        "unhealthy": "❌",
        "unknown": "❓"
    }
    
    lines = []
    lines.append(f"**ZeroClaw Health Check**")
    lines.append(f"*Время:* {timestamp}")
    lines.append(f"*Общий статус:* {status_emojis.get(overall, '❓')} {overall.upper()}")
    lines.append(f"*Время проверки:* {response_time} мс")
    lines.append("")
    
    services = data.get("services", {})
    
    for service_name, service_data in services.items():
        service_status = service_data.get("status", "unknown")
        service_emoji = status_emojis.get(service_status, "❓")
        service_time = service_data.get("response_time_ms", 0)
        
        lines.append(f"**{service_emoji} {service_name.upper()}** ({service_time} мс)")
        
        if service_name == "currency":
            details = service_data.get("details", {})
            for source, source_data in details.items():
                source_available = source_data.get("available", False)
                source_emoji = "✅" if source_available else "❌"
                source_time = source_data.get("response_time_ms", 0)
                error = source_data.get("error")
                
                status_text = f"{source_emoji} {source} ({source_time} мс)"
                if error and not source_available:
                    status_text += f" - {error}"
                lines.append(f"  {status_text}")
        
        elif service_name == "tts":
            details = service_data.get("details", "Нет информации")
            generation = service_data.get("generation", {})
            gen_status = generation.get("status", "unknown")
            gen_emoji = status_emojis.get(gen_status, "❓")
            gen_time = generation.get("response_time_ms", 0)
            
            lines.append(f"  📢 {details}")
            lines.append(f"  {gen_emoji} Генерация речи ({gen_time} мс)")
            if generation.get("error"):
                lines.append(f"  ⚠️ Ошибка: {generation['error']}")
        
        elif service_name == "web":
            details = service_data.get("details", {})
            for site, site_data in details.items():
                site_available = site_data.get("available", False)
                site_emoji = "✅" if site_available else "❌"
                site_time = site_data.get("response_time_ms", 0)
                error = site_data.get("error")
                
                status_text = f"{site_emoji} {site} ({site_time} мс)"
                if error and not site_available:
                    status_text += f" - {error}"
                lines.append(f"  {status_text}")
        
        lines.append("")
    
    # Рекомендации
    recommendations = []
    
    if overall == "unhealthy":
        recommendations.append("⚠️ *Критические проблемы!* Некоторые сервисы недоступны.")
    elif overall == "degraded":
        recommendations.append("⚠️ *Есть проблемы!* Некоторые сервисы работают с ограничениями.")
    
    # Проверяем конкретные проблемы
    if services.get("currency", {}).get("status") == "unhealthy":
        recommendations.append("• Курсы валют недоступны. Проверьте интернет-соединение.")
    
    if services.get("tts", {}).get("status") == "unhealthy":
        recommendations.append("• TTS сервис недоступен. Установите edge-tts: `pip install edge-tts`")
    
    if services.get("web", {}).get("status") == "unhealthy":
        recommendations.append("• Проблемы с веб-доступностью. Проверьте интернет-соединение и прокси.")
    
    if recommendations:
        lines.append("**Рекомендации:**")
        for rec in recommendations:
            lines.append(rec)
    
    return "\n".join(lines)

def main():
    """
    Точка входа для CLI
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='ZeroClaw Health Check')
    parser.add_argument('--service', choices=['currency', 'tts', 'web', 'all'], 
                       default='all', help='Сервис для проверки')
    parser.add_argument('--json', action='store_true', help='Вывод в JSON формате')
    parser.add_argument('--test-currency', action='store_true', help='Тест проверки валют')
    parser.add_argument('--test-tts', action='store_true', help='Тест проверки TTS')
    parser.add_argument('--test-web', action='store_true', help='Тест проверки веб-доступности')
    
    args = parser.parse_args()
    
    if args.test_currency:
        result = check_currency()
    elif args.test_tts:
        result = check_tts()
    elif args.test_web:
        result = check_web()
    elif args.service == 'currency':
        result = check_currency()
    elif args.service == 'tts':
        result = check_tts()
    elif args.service == 'web':
        result = check_web()
    else:
        result = check_all()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if args.service == 'all' and not (args.test_currency or args.test_tts or args.test_web):
            print(format_healthcheck_response(result))
        else:
            # Для отдельных сервисов простой вывод
            print(f"Статус: {result.get('status', 'unknown')}")
            print(f"Время ответа: {result.get('response_time_ms', 0)} мс")
            if 'details' in result:
                print("Детали:", json.dumps(result['details'], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()