#!/bin/bash

# 🚀 ZeroClaw Configuration Restore Script
# Автор: ZeroClaw
# Дата: 11 марта 2026

echo "========================================="
echo "🚀 ВОССТАНОВЛЕНИЕ KONФИГУРАЦИИ ZEROCLAW"
echo "========================================="

# Проверка прав
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Требуются права root. Запустите с sudo."
    exit 1
fi

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "\n${YELLOW}🔧 Шаг $1: $2${NC}"
}

# Переменные
ZEROCLAW_HOME="/root/.zeroclaw"
BACKUP_DIR="$(dirname "$0")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/tmp/zeroclaw_restore_${TIMESTAMP}.log"

# Начало логгирования
exec > >(tee -a "$LOG_FILE") 2>&1

echo "📝 Логи восстановления: $LOG_FILE"
echo "📦 Директория бэкапа: $BACKUP_DIR"
echo "🏠 Целевая директория: $ZEROCLAW_HOME"

# ==================== ШАГ 1: ПРОВЕРКА СИСТЕМЫ ====================

print_step "1" "Проверка системных зависимостей"

# Проверка Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python $PYTHON_VERSION установлен"
else
    print_error "Python3 не установлен"
    echo "Установка Python3..."
    apt update && apt install -y python3 python3-pip || yum install -y python3 python3-pip
fi

# Проверка pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 установлен"
else
    print_warning "pip3 не установлен, устанавливаю..."
    apt install -y python3-pip || yum install -y python3-pip
fi

# Проверка git
if command -v git &> /dev/null; then
    print_success "Git установлен"
else
    print_warning "Git не установлен, устанавливаю..."
    apt install -y git || yum install -y git
fi

# ==================== ШАГ 2: УСТАНОВКА ЗАВИСИМОСТЕЙ ====================

print_step "2" "Установка Python зависимостей"

REQUIRED_PACKAGES=(
    "PyPDF2"
    "python-docx"
    "vosk"
    "telebot"
    "pydub"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_success "$package уже установлен"
    else
        print_warning "Устанавливаю $package..."
        pip3 install "$package" || print_error "Не удалось установить $package"
    fi
done

# ==================== ШАГ 3: ВОССТАНОВЛЕНИЕ КОНФИГУРАЦИИ ====================

print_step "3" "Восстановление конфигурационных файлов"

# Создание директорий
mkdir -p "$ZEROCLAW_HOME"
mkdir -p "$ZEROCLAW_HOME/workspace"
mkdir -p "$ZEROCLAW_HOME/workspace/skills"
mkdir -p "$ZEROCLAW_HOME/workspace/telegram_files"
mkdir -p "$ZEROCLAW_HOME/workspace/memory"

# Копирование файлов
FILES_TO_COPY=(
    "AGENTS.md"
    "SOUL.md"
    "USER.md"
    "TOOLS.md"
    "IDENTITY.md"
    "MEMORY.md"
    "README.md"
    "SETUP.md"
    "config.toml"
    "voice_processor.py"
    "telegram_voice_handler.py"
    "pdf_parser.py"
    "docx_processor.py"
    "currency_helper.py"
)

for file in "${FILES_TO_COPY[@]}"; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        cp "$BACKUP_DIR/$file" "$ZEROCLAW_HOME/workspace/"
        print_success "Скопирован $file"
    else
        print_warning "Файл $file не найден в бэкапе"
    fi
done

# Копирование skills
if [ -d "$BACKUP_DIR/skills" ]; then
    cp -r "$BACKUP_DIR/skills" "$ZEROCLAW_HOME/workspace/"
    print_success "Скопированы skills"
fi

# ==================== ШАГ 4: УСТАНОВКА МОДЕЛИ VOSK ====================

print_step "4" "Установка модели распознавания речи Vosk"

VOSK_MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
VOSK_MODEL_DIR="/opt/vosk-model-ru"

if [ -d "$VOSK_MODEL_DIR" ]; then
    print_success "Модель Vosk уже установлена в $VOSK_MODEL_DIR"
else
    print_warning "Скачиваю модель Vosk..."
    
    # Скачивание
    wget -q "$VOSK_MODEL_URL" -O /tmp/vosk-model.zip
    if [ $? -eq 0 ]; then
        # Распаковка
        unzip -q /tmp/vosk-model.zip -d /tmp/
        mv /tmp/vosk-model-small-ru-0.22 "$VOSK_MODEL_DIR"
        rm /tmp/vosk-model.zip
        
        # Создание симлинка
        ln -sf "$VOSK_MODEL_DIR" "$ZEROCLAW_HOME/workspace/model_vosk_ru"
        
        print_success "Модель Vosk установлена"
    else
        print_error "Не удалось скачать модель Vosk"
    fi
fi

# ==================== ШАГ 5: НАСТРОЙКА TELEGRAM БОТА ====================

print_step "5" "Настройка Telegram бота"

TELEGRAM_CONFIG="$ZEROCLAW_HOME/config.toml"

if [ -f "$TELEGRAM_CONFIG" ]; then
    # Проверка токена в конфиге
    if grep -q "token = " "$TELEGRAM_CONFIG"; then
        print_success "Telegram токен найден в конфиге"
    else
        print_warning "Telegram токен не найден в конфиге"
        echo "Добавьте токен в $TELEGRAM_CONFIG:"
        echo ""
        echo "[telegram]"
        echo 'token = "ВАШ_ТОКЕН"'
        echo 'allowed_users = [480568670]'
        echo ""
    fi
else
    print_error "Конфигурационный файл не найден"
fi

# ==================== ШАГ 6: СОЗДАНИЕ .ENV ФАЙЛА ====================

print_step "6" "Создание файла окружения"

ENV_FILE="$ZEROCLAW_HOME/.env"

cat > "$ENV_FILE" << EOF
# ZeroClaw Environment Configuration
# Generated: $(date)

# Telegram
TELEGRAM_BOT_TOKEN=8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0

# Vosk Model
VOSK_MODEL_PATH=/opt/vosk-model-ru

# Workspace
ZEROCLAW_WORKSPACE=$ZEROCLAW_HOME/workspace

# User Settings
USER_ID=480568670
USER_NAME=root
TIMEZONE=UTC+5

# Logging
LOG_LEVEL=INFO
LOG_FILE=$ZEROCLAW_HOME/zeroclaw.log

# Security
SECRET_KEY_FILE=$ZEROCLAW_HOME/.secret_key
EOF

print_success "Файл окружения создан: $ENV_FILE"

# ==================== ШАГ 7: НАСТРОЙКА ПРАВ ДОСТУПА ====================

print_step "7" "Настройка прав доступа"

# Права на конфигурационные файлы
chmod 600 "$ZEROCLAW_HOME/config.toml"
chmod 600 "$ZEROCLAW_HOME/.env"

# Создание секретного ключа если нет
if [ ! -f "$ZEROCLAW_HOME/.secret_key" ]; then
    openssl rand -base64 32 > "$ZEROCLAW_HOME/.secret_key"
    chmod 600 "$ZEROCLAW_HOME/.secret_key"
    print_success "Секретный ключ создан"
fi

# Права на рабочую директорию
chmod -R 755 "$ZEROCLAW_HOME/workspace"
chown -R root:root "$ZEROCLAW_HOME"

print_success "Права доступа настроены"

# ==================== ШАГ 8: ТЕСТИРОВАНИЕ ====================

print_step "8" "Тестирование установки"

# Тест Python зависимостей
echo "🔍 Проверка Python зависимостей..."
python3 -c "
import sys
packages = ['PyPDF2', 'docx', 'vosk', 'telebot', 'pydub']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} импортирован успешно')
    except ImportError as e:
        print(f'❌ Ошибка импорта {pkg}: {e}')
"

# Тест модели Vosk
if [ -d "$VOSK_MODEL_DIR" ]; then
    echo "🔍 Проверка модели Vosk..."
    if [ -f "$VOSK_MODEL_DIR/am/final.mdl" ]; then
        print_success "Модель Vosk корректна"
    else
        print_error "Модель Vosk повреждена"
    fi
fi

# Тест конфигурации
if [ -f "$TELEGRAM_CONFIG" ]; then
    echo "🔍 Проверка конфигурации..."
    if python3 -c "import toml; toml.load('$TELEGRAM_CONFIG'); print('✅ Конфиг TOML валиден')" 2>/dev/null; then
        print_success "Конфигурационный файл валиден"
    else
        print_error "Ошибка в конфигурационном файле"
    fi
fi

# ==================== ШАГ 9: СОЗДАНИЕ SYSTEMD СЕРВИСА ====================

print_step "9" "Создание systemd сервиса (опционально)"

SERVICE_FILE="/etc/systemd/system/zeroclaw.service"

if [ ! -f "$SERVICE_FILE" ]; then
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=ZeroClaw AI Assistant
After=network.target
Requires=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$ZEROCLAW_HOME
EnvironmentFile=$ZEROCLAW_HOME/.env
ExecStart=/usr/local/bin/zeroclaw --config $ZEROCLAW_HOME/config.toml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=zeroclaw

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    print_success "Systemd сервис создан"
    
    echo "Для запуска сервиса выполните:"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable zeroclaw"
    echo "  sudo systemctl start zeroclaw"
else
    print_success "Systemd сервис уже существует"
fi

# ==================== ШАГ 10: ИТОГИ ====================

print_step "10" "Итоги восстановления"

echo ""
echo "========================================="
echo "🎉 ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО!"
echo "========================================="
echo ""
echo "📊 Сводка:"
echo "  ✅ Конфигурационные файлы восстановлены"
echo "  ✅ Python зависимости установлены"
echo "  ✅ Модель Vosk установлена"
echo "  ✅ Файл окружения создан"
echo "  ✅ Права доступа настроены"
echo ""
echo "📁 Директории:"
echo "  Конфигурация: $ZEROCLAW_HOME"
echo "  Рабочая: $ZEROCLAW_HOME/workspace"
echo "  Модель Vosk: $VOSK_MODEL_DIR"
echo ""
echo "🚀 Следующие шаги:"
echo "  1. Проверьте Telegram токен в config.toml"
echo "  2. Запустите ZeroClaw:"
echo "     systemctl start zeroclaw"
echo "  3. Проверьте логи:"
echo "     journalctl -u zeroclaw -f"
echo ""
echo "📝 Логи восстановления: $LOG_FILE"
echo "========================================="

# Создание файла с итоговой информацией
SUMMARY_FILE="$ZEROCLAW_HOME/RESTORE_SUMMARY.md"
cat > "$SUMMARY_FILE" << EOF
# ZeroClaw Restore Summary
## Дата восстановления: $(date)

## Установленные компоненты:
- Конфигурация: $ZEROCLAW_HOME
- Модель Vosk: $VOSK_MODEL_DIR
- Python пакеты: PyPDF2, python-docx, vosk, telebot, pydub

## Файлы:
- Конфиг: $ZEROCLAW_HOME/config.toml
- Окружение: $ZEROCLAW_HOME/.env
- Секретный ключ: $ZEROCLAW_HOME/.secret_key

## Навыки:
- Assistant: $ZEROCLAW_HOME/workspace/skills/assistant/
- Currency: $ZEROCLAW_HOME/workspace/skills/currency/

## Модули:
- Голосовая обработка: voice_processor.py
- Telegram интеграция: telegram_voice_handler.py
- PDF парсер: pdf_parser.py
- DOCX обработчик: docx_processor.py
- Валюты: currency_helper.py

## Для запуска:
\`\`\`bash
systemctl start zeroclaw
journalctl -u zeroclaw -f
\`\`\`

## Для проверки:
1. Отправьте сообщение в Telegram боту
2. Проверьте распознавание голосовых
3. Проверьте парсинг PDF
4. Проверьте курсы валют (/kz)

## Контакты:
- Пользователь ID: 480568670
- Бот: @null_clow_bot
EOF

print_success "Создан файл с итогами: $SUMMARY_FILE"

exit 0