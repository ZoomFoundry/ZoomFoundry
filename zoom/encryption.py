"""
    zoom encryption
"""

import os
from cryptography.fernet import Fernet


key_name = 'zoom_encryption_key'


def generate_key():
    """Generate a new key"""
    return Fernet.generate_key()


def get_encryption_key(key_name=key_name):
    """Get site encryption key"""

    def get_key_from_file(name):
        if name.isalpha:
            path = os.environ.get('ZOOM_SECRETS_PATH', '/run/secrets')
            pathname = os.path.join(path, name)
            if os.path.isfile(pathname):
                with open(pathname, 'r') as f:
                    return f.read()

    str_key = get_key_from_file(key_name) or os.environ.get(key_name.upper(), None)

    return str_key.encode() if str_key is not None else None


class Enpcrypter:

    def __init__(self, key):
        self.cypher = Fernet(key)

    def encrypt(self, value):
        encrypted_value = self.cypher.encrypt(value.encode('utf-8'))
        return encrypted_value

    def decrypt(self, encrypted_value):
        value = self.cypher.decrypt(encrypted_value).decode('utf-8')
        return value


def get_encrypter(key):
    return Enpcrypter(key)
