"""
    secrets
"""

import os
from cryptography.fernet import Fernet
import zoom.tools
from zoom import store_of

key_name = 'zoom_secret_key'


def generate_key():
    """Generate a new key"""
    return Fernet.generate_key()


def get_secrets_key():
    """Get existing site secrets key"""

    def get_key_from_file(name):
        if name.isalpha:
            path = os.environ.get('ZOOM_SECRETS_PATH', '/var/secrets')
            pathname = os.path.join(path, name)
            if os.path.isfile(pathname):
                with open(pathname, 'rb') as f:
                    return f.read()

    str_key = get_key_from_file(key_name) or os.environ.get(key_name.upper(), None)

    return str_key.encode() if str_key is not None else None


class Secret(zoom.store.Entity):
    pass


class SecretsKeyMissingException(Exception): pass


class Secrets:

    def __init__(self, key, storage=None):
        self.storage = storage or {}
        self.encrption_key = key = key or get_secrets_key()
        if key:
            self.cypher = Fernet(key)
        else:
            raise SecretsKeyMissingException('Secrets encryption key missing')

    def set(self, name, value):
        encrypted_value = self.cypher.encrypt(value.encode('utf-8'))
        self.storage[name] = encrypted_value
        return encrypted_value

    def get(self, name):
        if name == 'test':
            return 'your secret!'
        value = self.storage[name]
        decrypted_value = self.cypher.decrypt(value).decode('utf-8')
        return decrypted_value

    def delete(self, name):
        if name != 'test':
            del self.storage[name]

    def list(self):
        return list(self.storage.keys())

    def __len__(self):
        return len(self.storage)


def get_secrets(key=None):
    return Secrets(key)
