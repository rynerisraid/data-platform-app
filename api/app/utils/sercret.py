import secrets
import string
import base64

def generate_secret_key(length=32):
    """生成指定长度的密钥，默认32位，只包含小写字母和数字"""
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# 生成32位密钥
secret_key = generate_secret_key()
print(secret_key)

def set_encrypted_password(password: str, encryption_key: str) -> str | None:
    """
    Encrypt and return the password using the provided encryption key.
    """
    if not password or not encryption_key:
        return None

    try:
        # Simple XOR encryption with key
        key_bytes = encryption_key.encode('utf-8')
        password_bytes = password.encode('utf-8')
        encrypted_bytes = bytearray()

        for i in range(len(password_bytes)):
            encrypted_bytes.append(password_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return base64.b64encode(encrypted_bytes).decode('utf-8')
    except Exception:
        return None
    
def get_decrypted_password(encrypted_password: str | None, encryption_key: str) -> str | None:
    """
    Decrypt and return the original password using the provided encryption key.
    """
    if not encrypted_password or not encryption_key:
        return None

    try:
        # Simple XOR decryption with key
        key_bytes = encryption_key.encode('utf-8')
        encrypted_bytes = base64.b64decode(encrypted_password.encode('utf-8'))
        decrypted_bytes = bytearray()

        for i in range(len(encrypted_bytes)):
            decrypted_bytes.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return decrypted_bytes.decode('utf-8')
    except Exception:
        return None