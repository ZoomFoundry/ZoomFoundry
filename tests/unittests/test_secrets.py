"""
    test secrets
"""

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# It's reasonable in this case.

import os
import unittest

import zoom.secrets


class TestSecrets(unittest.TestCase):
    """test the Storage class"""

    def test_generate_key(self):
        key = zoom.secrets.generate_key()
        key_name = zoom.secrets.key_name.upper()
        self.assertEqual(type(key), type(b''))
        self.assertEqual(len(key), 44)

    def test_get_secrets_key(self):
        key = zoom.secrets.get_secrets_key()
        self.assertIsNone(key)

        key_name = zoom.secrets.key_name.upper()
        new_key = zoom.secrets.generate_key()
        os.environ.setdefault(key_name, new_key.decode())
        key = zoom.secrets.get_secrets_key()
        self.assertIsNotNone(key)

    def test_secrets_key_missing(self):
        del os.environ[zoom.secrets.key_name.upper()]
        key = zoom.secrets.get_secrets_key()
        self.assertIsNone(key)

    def test_set_get_secret(self):
        key = zoom.secrets.generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'
        my_encrypted_secret = secrets.set('my-secret', my_secret)
        self.assertNotEqual(my_secret, my_encrypted_secret)

        returned_value = secrets.get('my-secret')
        self.assertEqual(my_secret, returned_value)

    def test_list_secrets(self):
        key = zoom.secrets.generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)
        secrets.set('my-3rd-secret', my_secret)

        self.assertEqual(secrets.list(), [
            'my-secret',
            'my-other-secret',
            'my-3rd-secret',
        ])

    def test_len_secrets(self):
        key = zoom.secrets.generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)

        self.assertEqual(len(secrets), 2)

    def test_delete_secret(self):
        key = zoom.secrets.generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)
        secrets.set('my-3rd-secret', my_secret)

        secrets.delete('my-other-secret')

        self.assertEqual(secrets.list(), [
            'my-secret',
            'my-3rd-secret',
        ])

