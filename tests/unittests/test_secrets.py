"""
    test secrets
"""

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# It's reasonable in this case.

import os
import unittest

import zoom.encryption
import zoom.secrets
import zoom.database
from zoom.encryption import generate_key

class TestSecrets(unittest.TestCase):
    """test the Storage class"""

    def setUp(self):
        db = zoom.database.setup_test()
        db.autocommit(1)
        zoom.system.site = self.site = site = zoom.sites.Site()
        self.store = zoom.store_of(zoom.secrets.Secret)
        self.store.zap()
        self.key_name = zoom.encryption.key_name + '_test'

    def test_get_encryption_key(self):
        key = zoom.encryption.get_encryption_key(self.key_name)
        self.assertIsNone(key)

        key_name = self.key_name.upper()
        new_key = generate_key()
        os.environ.setdefault(key_name, new_key.decode())
        key = zoom.encryption.get_encryption_key(self.key_name)
        self.assertIsNotNone(key)

    def test_secrets_key_missing(self):
        del os.environ[self.key_name.upper()]
        key = zoom.encryption.get_encryption_key(self.key_name)
        self.assertIsNone(key)

    def test_connection(self):
        self.assertEqual(len(zoom.db('show tables')), 9)

    def test_set_get_secret(self):
        key = generate_key()
        secrets = zoom.secrets.get_secrets(key, self.store)
        my_secret = 'my secret'
        my_encrypted_secret = secrets.set('my-secret', my_secret)
        self.assertNotEqual(my_secret, my_encrypted_secret)

        # print(zoom.secrets.get_secrets(key))
        # print(zoom.store_of(zoom.secrets.Secret))

        returned_value = secrets.get('my-secret')
        self.assertEqual(my_secret, returned_value)


    def test_keys(self):
        key = generate_key()
        secrets = zoom.secrets.get_secrets(key, self.store)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)
        secrets.set('my-3rd-secret', my_secret)

        self.assertEqual(secrets.keys(), [
            'my-secret',
            'my-other-secret',
            'my-3rd-secret',
        ])

    def test_len_secrets(self):
        key = generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)

        self.assertEqual(len(secrets), 2)

    def test_delete_secret(self):
        key = generate_key()
        secrets = zoom.secrets.get_secrets(key)
        my_secret = 'my secret'

        secrets.set('my-secret', my_secret)
        secrets.set('my-other-secret', my_secret)
        secrets.set('my-3rd-secret', my_secret)

        secrets.delete('my-other-secret')

        self.assertEqual(secrets.keys(), [
            'my-secret',
            'my-3rd-secret',
        ])

