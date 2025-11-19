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
        self.storage = storage or store_of(Secret)
        self.encrption_key = key = key or get_secrets_key()
        if key:
            self.cypher = Fernet(key)
        else:
            raise SecretsKeyMissingException('Secrets encryption key missing')

    def set(self, name, value):
        encrypted_value = self.cypher.encrypt(value.encode('utf-8'))
        self.storage.put(
            Secret(
                name=name,
                value=encrypted_value
            ),
        )
        return encrypted_value

    def get(self, name):
        record = self.storage.first(name=name)
        if record:
            encrypted_value = record.value
            value = self.cypher.decrypt(encrypted_value).decode('utf-8')
            return value

    def delete(self, name):
        self.storage.delete(name=name)

    def keys(self):
        return list(s.name for s in self.storage)

    def list(self):
        return list(self.storage)

    def __len__(self):
        return len(self.storage)

    def __str__(self):

        return '\nSecrets\n--------------\n' + ''.join(
            f'{secret.name}'
            for secret in self.list()
        )


def get_secrets(key=None, storage=None):
    return Secrets(key, storage)

