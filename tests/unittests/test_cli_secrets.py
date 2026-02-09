import os
import sys
import tempfile
import configparser
import unittest
from unittest.mock import patch

from zoom.cli.secrets import secrets

class TestCliSecrets(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.site_ini = os.path.join(self.tmpdir.name, 'site.ini')
        with open(self.site_ini, 'w') as f:
            f.write('[site]\nname=TEST\n')

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_new_key_creates_key(self):
        argv = ['zoom', 'secrets', 'new-key', '--site', self.tmpdir.name]
        with patch.object(sys, 'argv', argv):
            with self.assertRaises(SystemExit) as cm:
                secrets()
        self.assertEqual(cm.exception.code, 0)
        cp = configparser.ConfigParser()
        cp.read(self.site_ini)
        self.assertTrue(cp.has_option('secrets', 'key'))

    def test_new_key_no_force_fails(self):
        # first run to create key
        argv1 = ['zoom', 'secrets', 'new-key', '--site', self.tmpdir.name]
        with patch.object(sys, 'argv', argv1):
            with self.assertRaises(SystemExit):
                secrets()
        # second run without --force should error
        argv2 = ['zoom', 'secrets', 'new-key', '--site', self.tmpdir.name]
        with patch.object(sys, 'argv', argv2):
            with self.assertRaises(SystemExit) as cm:
                secrets()
        self.assertNotEqual(cm.exception.code, 0)

    def test_new_key_with_force_overwrites(self):
        argv1 = ['zoom', 'secrets', 'new-key', '--site', self.tmpdir.name]
        with patch.object(sys, 'argv', argv1):
            with self.assertRaises(SystemExit):
                secrets()
        cp = configparser.ConfigParser()
        cp.read(self.site_ini)
        old_key = cp.get('secrets', 'key')
        # run again with --force
        argv2 = ['zoom', 'secrets', 'new-key', '--site', self.tmpdir.name, '--force']
        with patch.object(sys, 'argv', argv2):
            with self.assertRaises(SystemExit) as cm:
                secrets()
        self.assertEqual(cm.exception.code, 0)
        cp.read(self.site_ini)
        self.assertNotEqual(cp.get('secrets', 'key'), old_key)
