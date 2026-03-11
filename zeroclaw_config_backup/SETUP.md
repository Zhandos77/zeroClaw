# 🚀 ИНСТРУКЦИЯ ПО ВОССТАНОВЛЕНИЮ ZEROCLAW

## 📦 Требования

### Системные зависимости:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg git

# CentOS/RHEL
sudo yum install -y python3-pip python3-venv ffmpeg git
```

### Python зависимости:
```bash
pip3 install PyPDF2 python-docx vosk telebot pydub
```

### Модель распознавания речи:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
unzip vosk-model-small-ru-0.22.zip
mv vosk-model-small-ru-0.22 /opt/vosk-model-ru
```

## 🔧 ШАГ ЗА ШАГОМ

### Шаг 1: Установка ZeroClaw
```bash
# Скачать ZeroClaw
git clone https://github.com/zeroclaw/zeroclaw.git
cd zeroclaw

# Создать конфигурационную директорию
mkdir -p ~/.zeroclaw
```

### Шаг 2: Восстановление конфигурации
```bash
# Скопировать все файлы из этого репозитория
cp -r zeroclaw_config_backup/* ~/.zeroclaw/

# Проверить права доступа
chmod 600 ~/.zeroclaw/config.toml
chmod 600 ~/.zeroclaw/.secret_key
```

### Шаг 3: Настройка Telegram бота

#### 1. Создать бота через @BotFather:
- Открыть Telegram
- Найти @BotFather
- Отправить `/newbot`
- Выбрать имя: `Null Claw Bot`
- Получить токен: `8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0`

#### 2. Настроить в config.toml:
```toml
[telegram]
token = "8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0"
allowed_users = [480568670]  # ID пользователя root
```

### Шаг 4: Настройка окружения

#### Создать .env файл:
```bash
cat > ~/.zeroclaw/.env << EOF
# Telegram
TELEGRAM_BOT_TOKEN=8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0

# Vosk модель
VOSK_MODEL_PATH=/opt/vosk-model-ru

# Рабочая директория
ZEROCLAW_WORKSPACE=~/.zeroclaw/workspace

# Пользовательские настройки
USER_ID=480568670
USER_NAME=root
TIMEZONE=UTC+5
EOF
```

### Шаг 5: Запуск ZeroClaw

#### Вариант A: Как сервис (рекомендуется)
```bash
# Создать systemd сервис
sudo tee /etc/systemd/system/zeroclaw.service << EOF
[Unit]
Description=ZeroClaw AI Assistant
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.zeroclaw
EnvironmentFile=/root/.zeroclaw/.env
ExecStart=/usr/local/bin/zeroclaw --config /root/.zeroclaw/config.toml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Запустить сервис
sudo systemctl daemon-reload
sudo systemctl enable zeroclaw
sudo systemctl start zeroclaw
sudo systemctl status zeroclaw
```

#### Вариант B: Вручную
```bash
# Активировать виртуальное окружение
python3 -m venv ~/.zeroclaw/venv
source ~/.zeroclaw/venv/bin/activate

# Запустить ZeroClaw
zeroclaw --config ~/.zeroclaw/config.toml
```

### Шаг 6: Проверка работы

#### 1. Проверить Telegram бота:
```bash
# Отправить тестовое сообщение
curl -X POST "https://api.telegram.org/bot8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0/sendMessage" \
  -d "chat_id=480568670&text=ZeroClaw восстановлен и готов к работе!"
```

#### 2. Проверить навыки:
- Отправить `/kz` — курсы валют Казахстана
- Отправить голосовое — проверить распознавание
- Отправить PDF — проверить парсинг

#### 3. Проверить логи:
```bash
journalctl -u zeroclaw -f
# или
tail -f ~/.zeroclaw/zeroclaw.log
```

## 🔍 РЕШЕНИЕ ПРОБЛЕМ

### Проблема 1: Telegram бот не отвечает
```bash
# Проверить токен
curl "https://api.telegram.org/bot8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0/getMe"

# Проверить вебхук
curl "https://api.telegram.org/bot8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0/getWebhookInfo"

# Очистить очередь сообщений
curl "https://api.telegram.org/bot8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0/getUpdates?offset=-1"
```

### Проблема 2: Не работает распознавание речи
```bash
# Проверить модель Vosk
python3 -c "import vosk; print('Vosk импортирован')"

# Проверить путь к модели
ls -la /opt/vosk-model-ru/

# Проверить ffmpeg
ffmpeg -version
```

### Проблема 3: Не парсятся PDF
```bash
# Проверить PyPDF2
python3 -c "import PyPDF2; print('PyPDF2 импортирован')"

# Проверить права доступа
ls -la /root/.zeroclaw/workspace/telegram_files/
```

### Проблема 4: Нет доступа к файлам
```bash
# Проверить владельца
ls -la /root/.zeroclaw/

# Исправить права
chown -R root:root /root/.zeroclaw/
chmod 755 /root/.zeroclaw/
chmod 600 /root/.zeroclaw/config.toml
```

## 📊 ТЕСТОВЫЕ КОМАНДЫ

### Тест голосового распознавания:
```bash
python3 ~/.zeroclaw/workspace/voice_processor.py --test
```

### Тест парсинга PDF:
```bash
python3 ~/.zeroclaw/workspace/pdf_parser.py --file /path/to/test.pdf
```

### Тест валют:
```bash
python3 ~/.zeroclaw/workspace/currency_helper.py --country KZ
```

## 🎯 КОНТАКТНАЯ ИНФОРМАЦИЯ

### Для восстановления доступа:
- **Telegram ID:** 480568670
- **Бот:** @null_clow_bot
- **Токен:** 8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0
- **Рабочая директория:** `/root/.zeroclaw/workspace`

### Резервные копии:
- **Конфигурация:** Этот репозиторий
- **Модели:** `/opt/vosk-model-ru`
- **Данные:** `/root/.zeroclaw/workspace/memory/`

## 🔄 АВТОМАТИЧЕСКОЕ ВОССТАНОВЛЕНИЕ

### Скрипт восстановления:
```bash
#!/bin/bash
# save as restore_zeroclaw.sh

echo "🚀 Начинаем восстановление ZeroClaw..."

# 1. Установка зависимостей
apt update && apt install -y python3-pip ffmpeg
pip3 install PyPDF2 python-docx vosk telebot

# 2. Восстановление конфигурации
mkdir -p ~/.zeroclaw
cp -r zeroclaw_config_backup/* ~/.zeroclaw/

# 3. Загрузка модели Vosk
wget -q https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
unzip -q vosk-model-small-ru-0.22.zip
mv vosk-model-small-ru-0.22 /opt/vosk-model-ru

# 4. Запуск
systemctl restart zeroclaw

echo "✅ ZeroClaw восстановлен!"
```

### Запуск скрипта:
```bash
chmod +x restore_zeroclaw.sh
./restore_zeroclaw.sh
```

---

**Дата создания:** 11 марта 2026  
**Для пользователя:** root (ID: 480568670)  
**Версия конфигурации:** 1.0