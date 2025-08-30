import secrets
import string

def generate_secret_key(length=32):
    """生成指定长度的密钥，默认32位，只包含小写字母和数字"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# 生成32位密钥
secret_key = generate_secret_key()
print(secret_key)
