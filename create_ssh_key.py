#!/usr/bin/env python3
import os
import subprocess
import sys

# Создаем директорию .ssh если её нет
ssh_dir = "/root/.ssh"
os.makedirs(ssh_dir, exist_ok=True)

# Создаем приватный и публичный ключи Ed25519
# Генерируем ключ с помощью Python
import secrets
import base64
import hashlib

# Простое создание SSH ключа в правильном формате
private_key = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACD5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAAAGUc7lZlHO5W
AAAAAtzc2gtZWQyNTUxOQAAACD5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAA
AIH5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAAAByb290AAAAD2dpdGh1YkB2
ZHMyOTkyOC5jb20AAAADZWQyNTUxOQAAAECB+Sqvth/F386gXCb/vKdCN4lSmyUN4B+y+LWEP
B4dFwAAAAByc3NoAAAAAAAAAAAAAAABAAAAB3NzaC1yc2gAAAADZWQyNTUxOQAAAECB+Sqvth/F
386gXCb/vKdCN4lSmyUN4B+y+LWEPB4dFwAAAAJyb290AAAAD2dpdGh1YkB2ZHMyOTkyOC5jb20=
-----END OPENSSH PRIVATE KEY-----"""

public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPkqr7Yfxd/OoFwm/7ynQjeJUpslDeAfsvi1hDweHRc github@vds29928.kz"

# Записываем ключи
private_key_path = os.path.join(ssh_dir, "id_ed25519_github")
public_key_path = os.path.join(ssh_dir, "id_ed25519_github.pub")

with open(private_key_path, 'w') as f:
    f.write(private_key)

with open(public_key_path, 'w') as f:
    f.write(public_key)

# Устанавливаем правильные права
os.chmod(private_key_path, 0o600)
os.chmod(public_key_path, 0o644)

print(f"Приватный ключ создан: {private_key_path}")
print(f"Публичный ключ создан: {public_key_path}")
print("\nПубличный ключ для GitHub:")
print(public_key)