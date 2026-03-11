#!/bin/bash
# Добавляем GitHub в known_hosts
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
echo "GitHub host key added to known_hosts"