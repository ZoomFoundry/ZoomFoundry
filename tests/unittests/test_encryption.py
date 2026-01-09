"""
    test encryption
"""

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# It's reasonable in this case.

import unittest

import zoom.encryption
# from zoom.database import setup_test


class TestSecrets(unittest.TestCase):
    """test the Storage class"""

    def setUp(self):
        self.key = zoom.encryption.generate_key()
        self.encrypter = zoom.encryption.get_encrypter(self.key)

    def test_generate_key(self):
        key = zoom.encryption.generate_key()
        self.assertEqual(type(key), type(b''))
        self.assertEqual(len(key), 44)

    def test_encrypt_decrypt(self):
        my_sensitive_data = 'my data'
        my_encrypted_sensitive_data = self.encrypter.encrypt(my_sensitive_data)
        self.assertNotEqual(my_sensitive_data, my_encrypted_sensitive_data)
        self.assertEqual(my_sensitive_data, self.encrypter.decrypt(my_encrypted_sensitive_data))


