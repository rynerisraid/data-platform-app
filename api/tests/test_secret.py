import sys
import os
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.sercret import set_encrypted_password, get_decrypted_password, generate_secret_key


def test_set_encrypted_password():
    """测试密码加密功能"""
    # 测试正常情况
    password = "test_password123"
    encryption_key = "test_key"
    
    encrypted = set_encrypted_password(password, encryption_key)
    assert encrypted is not None
    assert isinstance(encrypted, str)
    assert encrypted != password  # 确保加密后的密码与原密码不同


def test_get_decrypted_password():
    """测试密码解密功能"""
    # 测试正常情况
    password = "test_password123"
    encryption_key = "test_key"
    
    # 先加密再解密
    encrypted = set_encrypted_password(password, encryption_key)
    assert encrypted is not None
    
    decrypted = get_decrypted_password(encrypted, encryption_key)
    assert decrypted is not None
    assert decrypted == password  # 确保解密后的密码与原密码相同


def test_encrypt_decrypt_with_different_keys():
    """测试使用不同密钥加密解密"""
    password = "test_password123"
    encryption_key1 = "test_key_1"
    encryption_key2 = "test_key_2"
    
    # 用不同密钥加密
    encrypted1 = set_encrypted_password(password, encryption_key1)
    encrypted2 = set_encrypted_password(password, encryption_key2)
    
    assert encrypted1 is not None
    assert encrypted2 is not None
    assert encrypted1 != encrypted2  # 确保使用不同密钥得到不同结果
    
    # 用对应密钥解密
    decrypted1 = get_decrypted_password(encrypted1, encryption_key1)
    decrypted2 = get_decrypted_password(encrypted2, encryption_key2)
    
    assert decrypted1 == password
    assert decrypted2 == password


def test_encrypt_decrypt_empty_values():
    """测试空值处理"""
    # 测试空密码
    encrypted = set_encrypted_password("", "test_key")
    assert encrypted is None
    
    # 测试空密钥
    encrypted = set_encrypted_password("test_password", "")
    assert encrypted is None
    
    # 测试空加密密码解密
    decrypted = get_decrypted_password(None, "test_key")
    assert decrypted is None
    
    # 测试空密钥解密
    decrypted = get_decrypted_password("encrypted_password", "")
    assert decrypted is None


def test_encrypt_decrypt_with_special_characters():
    """测试特殊字符密码加密解密"""
    password = "p@ssw0rd!#$%^&*()"
    encryption_key = "special_key_!@#$"
    
    encrypted = set_encrypted_password(password, encryption_key)
    assert encrypted is not None
    
    decrypted = get_decrypted_password(encrypted, encryption_key)
    assert decrypted is not None
    assert decrypted == password


def test_encrypt_decrypt_with_long_password():
    """测试长密码加密解密"""
    password = "a" * 1000  # 1000个字符的长密码
    encryption_key = generate_secret_key()
    
    encrypted = set_encrypted_password(password, encryption_key)
    assert encrypted is not None
    
    decrypted = get_decrypted_password(encrypted, encryption_key)
    assert decrypted is not None
    assert decrypted == password


def test_encrypt_decrypt_with_chinese_characters():
    """测试中文密码加密解密"""
    password = "测试密码123"
    encryption_key = "测试密钥"
    
    encrypted = set_encrypted_password(password, encryption_key)
    assert encrypted is not None
    
    decrypted = get_decrypted_password(encrypted, encryption_key)
    assert decrypted is not None
    assert decrypted == password