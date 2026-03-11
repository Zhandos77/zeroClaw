#!/bin/bash

# 📦 ZeroClaw Backup Packing Script
# Создает архив со всей конфигурацией

echo "========================================="
echo "📦 УПАКОВКА БЭКАПА ZEROCLAW"
echo "========================================="

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_step() {
    echo -e "\n${YELLOW}🔧 $1${NC}"
}

# Переменные
BACKUP_DIR="$(dirname "$0")"
PARENT_DIR="$(dirname "$BACKUP_DIR")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="zeroclaw_config_${TIMESTAMP}.tar.gz"
FULL_ARCHIVE_PATH="$PARENT_DIR/$ARCHIVE_NAME"

print_step "1. Подготовка директории бэкапа"

# Проверка существования файлов
ESSENTIAL_FILES=(
    "config.toml"
    "AGENTS.md"
    "SOUL.md"
    "USER.md"
    "TOOLS.md"
    "IDENTITY.md"
    "MEMORY.md"
    "README.md"
    "SETUP.md"
    "restore.sh"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$BACKUP_DIR/$file" ]; then
        print_success "Найден $file"
    else
        echo "⚠️  Отсутствует $file"
    fi
done

# Проверка директорий
if [ -d "$BACKUP_DIR/skills" ]; then
    print_success "Директория skills найдена"
else
    echo "⚠️  Отсутствует директория skills"
fi

print_step "2. Создание архива"

cd "$BACKUP_DIR" || exit 1

# Создаем архив
tar -czf "$FULL_ARCHIVE_PATH" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="*.log" \
    --exclude="*.tmp" \
    .

if [ $? -eq 0 ]; then
    print_success "Архив создан: $ARCHIVE_NAME"
    
    # Информация об архиве
    ARCHIVE_SIZE=$(du -h "$FULL_ARCHIVE_PATH" | cut -f1)
    FILE_COUNT=$(tar -tzf "$FULL_ARCHIVE_PATH" | wc -l)
    
    echo ""
    echo "📊 Информация об архиве:"
    echo "   Имя: $ARCHIVE_NAME"
    echo "   Размер: $ARCHIVE_SIZE"
    echo "   Файлов: $FILE_COUNT"
    echo "   Путь: $FULL_ARCHIVE_PATH"
else
    echo "❌ Ошибка при создании архива"
    exit 1
fi

print_step "3. Проверка архива"

# Проверяем что архив можно распаковать
TEST_DIR="/tmp/zeroclaw_test_${TIMESTAMP}"
mkdir -p "$TEST_DIR"
tar -xzf "$FULL_ARCHIVE_PATH" -C "$TEST_DIR" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Архив проверен, можно распаковать"
    
    # Проверяем ключевые файлы
    TEST_FILES=(
        "$TEST_DIR/config.toml"
        "$TEST_DIR/restore.sh"
        "$TEST_DIR/README.md"
    )
    
    for test_file in "${TEST_FILES[@]}"; do
        if [ -f "$test_file" ]; then
            print_success "Файл $(basename "$test_file") присутствует в архиве"
        fi
    done
    
    # Очистка тестовой директории
    rm -rf "$TEST_DIR"
else
    echo "❌ Архив поврежден или не может быть распакован"
    exit 1
fi

print_step "4. Создание checksum"

# Создаем контрольную сумму
MD5_FILE="$PARENT_DIR/${ARCHIVE_NAME}.md5"
md5sum "$FULL_ARCHIVE_PATH" > "$MD5_FILE"
print_success "Контрольная сумма создана: $(basename "$MD5_FILE")"

print_step "5. Инструкция по использованию"

echo ""
echo "========================================="
echo "📋 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ БЭКАПА"
echo "========================================="
echo ""
echo "1. 📦 Скачайте архив:"
echo "   $ARCHIVE_NAME"
echo ""
echo "2. 📂 Распакуйте:"
echo "   tar -xzf $ARCHIVE_NAME"
echo ""
echo "3. 🚀 Восстановите:"
echo "   cd zeroclaw_config_backup"
echo "   sudo ./restore.sh"
echo ""
echo "4. 🔍 Проверьте контрольную сумму:"
echo "   md5sum -c ${ARCHIVE_NAME}.md5"
echo ""
echo "5. 📁 Структура архива:"
echo "   ├── config.toml          # Основная конфигурация"
echo "   ├── restore.sh           # Скрипт восстановления"
echo "   ├── README.md           # Документация"
echo "   ├── SETUP.md            # Инструкция по установке"
echo "   ├── skills/             # Установленные навыки"
echo "   ├── voice_processor.py  # Обработка голосовых"
echo "   └── ...                 # Остальные файлы"
echo ""
echo "========================================="
echo "🎉 БЭКАП ГОТОВ К ИСПОЛЬЗОВАНИЮ!"
echo "========================================="

# Создаем простой скрипт для скачивания и восстановления
cat > "$PARENT_DIR/quick_restore.md" << EOF
# 🚀 Быстрое восстановление ZeroClaw

## Шаг 1: Скачайте архив
\`\`\`bash
# Скачайте архив с бэкапом
wget [URL_К_АРХИВУ]/$ARCHIVE_NAME
wget [URL_К_АРХИВУ]/${ARCHIVE_NAME}.md5
\`\`\`

## Шаг 2: Проверьте целостность
\`\`\`bash
md5sum -c ${ARCHIVE_NAME}.md5
# Должно вывести: $ARCHIVE_NAME: OK
\`\`\`

## Шаг 3: Распакуйте
\`\`\`bash
tar -xzf $ARCHIVE_NAME
cd zeroclaw_config_backup
\`\`\`

## Шаг 4: Восстановите
\`\`\`bash
sudo ./restore.sh
\`\`\`

## Шаг 5: Запустите
\`\`\`bash
systemctl start zeroclaw
journalctl -u zeroclaw -f
\`\`\`

## Контакты
- Пользователь: root (ID: 480568670)
- Бот: @null_clow_bot
- Токен: 8666797061:AAE-dCRGyfeS-zdP8847en8E6inuH402rk0

## Для проверки
1. Отправьте сообщение боту в Telegram
2. Проверьте команды: /kz, /ru
3. Отправьте голосовое сообщение
4. Отправьте PDF документ
EOF

print_success "Создана инструкция быстрого восстановления: quick_restore.md"

exit 0