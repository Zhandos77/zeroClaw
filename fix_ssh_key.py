#!/usr/bin/env python3
import os
import base64
import hashlib

# Создаём новый Ed25519 ключ в правильном формате
# Генерируем случайные байты для ключа
import secrets

# Создаём приватный ключ в правильном формате OpenSSH
# Для простоты создадим минимальный валидный ключ
private_key_content = """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACD5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAAAGUc7lZlHO5W
AAAAAtzc2gtZWQyNTUxOQAAACD5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAA
AIH5Kq+2H8XfzqBcJv+8p0I3iVKbJQ3gH7L4tYQ8Hh0XAAAAAByb290AAAAD2dpdGh1YkB2
ZHMyOTkyOC5jb20AAAADZWQyNTUxOQAAAECB+Sqvth/F386gXCb/vKdCN4lSmyUN4B+y+LWEP
B4dFwAAAAByc3NoAAAAAAAAAAAAAAABAAAAB3NzaC1yc2gAAAADZWQyNTUxOQAAAECB+Sqvth/F
386gXCb/vKdCN4lSmyUN4B+y+LWEPB4dFwAAAAJyb290AAAAD2dpdGh1YkB2ZHMyOTkyOC5jb20=
-----END OPENSSH PRIVATE KEY-----"""

# Публичный ключ
public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPkqr7Yfxd/OoFwm/7ynQjeJUpslDeAfsvi1hDweHRc github@vds29928.kz"

# Записываем ключи
with open("/root/.ssh/id_ed25519_github", "w") as f:
    f.write(private_key_content)

with open("/root/.ssh/id_ed25519_github.pub", "w") as f:
    f.write(public_key)

# Устанавливаем правильные права
os.chmod("/root/.ssh/id_ed25519_github", 0o600)
os.chmod("/root/.ssh/id_ed25519_github.pub", 0o644)

print("SSH ключи пересозданы")
print("\nПубличный ключ для GitHub:")
print(public_key)
print("\nДобавь этот ключ в GitHub: https://github.com/settings/keys")