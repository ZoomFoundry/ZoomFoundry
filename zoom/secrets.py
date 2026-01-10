"""
    secrets
"""

import os
import zoom
from zoom.encryption import get_encrypter, get_encryption_key
from zoom import store_of


class Secret(zoom.store.Entity):

    @property
    def key(self):
        return self.name

    @property
    def url(self):
        return f'/secrets/{self.key}'

    @property
    def link(self):
        # return self.name
        return zoom.link_to(self.name, self.url)


class SecretsKeyMissingException(Exception): pass


class Secrets:

    def __init__(self, key, storage=None):
        self.storage = storage or store_of(Secret)
        self.encrption_key = key = key or get_encryption_key()
        if key:
            self.encrypter = get_encrypter(key)
        else:
            raise SecretsKeyMissingException('Secrets encryption key missing')

    def set(self, name, value):
        encrypted_value = self.encrypter.encrypt(value)
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
            value = self.encrypter.decrypt(encrypted_value)
            return value

    def delete(self, name):
        self.storage.delete(name=name)

    def keys(self):
        return list(s.name for s in self.storage)

    def list(self):
        return list(self.storage)

    def first(self, name):
        return self.storage.first(name=name)

    def __iter__(self):
        return self.storage.__iter__()

    def __len__(self):
        return len(self.storage)

    def __str__(self):

        return '\nSecrets\n--------------\n' + ''.join(
            f'{secret.name}'
            for secret in self.list()
        )


def get_secrets(key=None, storage=None):
    return Secrets(key, storage)


def get_secrets_store():
    return store_of(Secret)