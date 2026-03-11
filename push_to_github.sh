#!/bin/bash
echo "=== Начинаем push в GitHub ==="
cd /root/.zeroclaw/workspace

echo "1. Проверяем SSH ключ..."
ssh -T git@github.com

echo "2. Добавляем файлы..."
git add .

echo "3. Создаём коммит..."
git commit -m "Initial commit: ZeroClaw configuration $(date '+%Y-%m-%d %H:%M:%S')"

echo "4. Делаем push..."
git push origin master

echo "5. Проверяем статус..."
git status

echo "=== Готово! ==="