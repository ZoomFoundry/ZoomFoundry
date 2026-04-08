"""
Usage:
  zoom secrets list [options]
  zoom secrets get [options] <name>
  zoom secrets set [options] <name> <value>
  zoom secrets delete [options] <name>
  zoom secrets rename [options] <old> <new>
  zoom secrets exists [options] <name>
  zoom secrets clear [options]
  zoom secrets new-key [options]
  zoom secrets rotate [options]

Options:
  -h --help            Show this help message.
  --site=<path>        Path to site directory.
  -k --key=<val>       Encryption key.
  --key-file=<path>    Read encryption key from file.
  -f --force           Overwrite existing key when using new-key.
  --reveal             Reveal secret values (for get).
  --json               Output machine-readable JSON.
  --quiet              Suppress output messages.
"""
from docopt import docopt
import json
import sys
import os
import configparser

from zoom.encryption import generate_key
from zoom.cli.common import finish
from zoom.sites import Site
from zoom.secrets import get_secrets, get_secrets_store, SecretsKeyMissingException
from zoom.database import DatabaseException


def secrets():
    args = docopt(__doc__)
    site_path = args.get('--site')
    site_path = os.path.expanduser(site_path)
    site_path = os.path.abspath(site_path)
    if not site_path:
        finish(True, 'Error: --site is required')



    # new-key subcommand: generate and save encryption key to site.ini
    if args['new-key']:
        ini_path = os.path.join(site_path, 'site.ini')
        cp = configparser.ConfigParser()
        cp.read(ini_path)
        if cp.has_option('secrets', 'key') and not args['--force']:
            finish(True, 'Secrets key already exists; use --force to overwrite')
        if not cp.has_section('secrets'):
            cp.add_section('secrets')
        newkey = generate_key().decode()
        cp.set('secrets', 'key', newkey)
        with open(ini_path, 'w') as f:
            cp.write(f)
        print(f'New secrets key generated and saved to {ini_path}')
        sys.exit(0)

    # rotate: re-encrypt all secrets under a new key
    if args['rotate']:
        if args.get('--key'):
            old_key = args['--key']
        elif args.get('--key-file'):
            try:
                old_key = open(args['--key-file']).read().strip()
            except Exception as e:
                finish(True, f'Error reading key file: {e}')
        else:
            ini_path = os.path.join(site_path, 'site.ini')
            cp = configparser.ConfigParser()
            cp.read(ini_path)
            if not cp.has_option('secrets', 'key'):
                finish(True, 'Secrets encryption key missing; provide --key or run new-key')
            old_key = cp.get('secrets', 'key')
        try:
            store = get_secrets_store()
            old_secrets = get_secrets(old_key, store)
        except SecretsKeyMissingException as e:
            finish(True, str(e))
        new_key = generate_key().decode()
        new_secrets = get_secrets(new_key, store)
        for name in old_secrets.keys():
            val = old_secrets.get(name)
            new_secrets.update(name, val)
        # persist new key
        ini_path = os.path.join(site_path, 'site.ini')
        cp = configparser.ConfigParser()
        cp.read(ini_path)
        if not cp.has_section('secrets'):
            cp.add_section('secrets')
        cp.set('secrets', 'key', new_key)
        with open(ini_path, 'w') as f:
            cp.write(f)
        print(f'Secrets rotated and new key saved to {ini_path}')
        sys.exit(0)

    site = Site(site_path)
    site.activate()

    # resolve key

    # resolve key
    key = args.get('--key')
    if args.get('--key-file'):
        try:
            key = open(args['--key-file']).read().strip()
        except Exception as e:
            finish(True, f'Error reading key file: {e}')

    try:
        store = get_secrets_store()
        secrets_obj = get_secrets(key, store)
    except SecretsKeyMissingException as e:
        finish(True, str(e))

    cmd = None
    for c in ('list', 'get', 'set', 'delete', 'rename', 'exists', 'clear'):
        if args[c]:
            cmd = c
            break

    try:
        if cmd == 'list':
            names = secrets_obj.keys()
            if args['--json']:
                print(json.dumps(names))
            else:
                for n in names:
                    print(n)

        elif cmd == 'get':
            name = args['<name>']
            val = secrets_obj.get(name)
            if val is None:
                finish(True, f'secret not found: {name}')
            out = val if args['--reveal'] else '****'
            if args['--json']:
                print(json.dumps({name: val}))
            elif not args['--quiet']:
                print(out)

        elif cmd == 'set':
            name = args['<name>']
            value = args['<value>']
            if value == '-':
                value = sys.stdin.read().rstrip('\n')
            secrets_obj.set(name, value)
            if not args['--quiet']:
                print(f'secret set: {name}')

        elif cmd == 'delete':
            name = args['<name>']
            secrets_obj.delete(name)
            if not args['--quiet']:
                print(f'secret deleted: {name}')

        elif cmd == 'rename':
            old = args['<old>']
            new = args['<new>']
            secrets_obj.rename(old, new)
            if not args['--quiet']:
                print(f'secret renamed: {old} -> {new}')

        elif cmd == 'exists':
            name = args['<name>']
            exists = secrets_obj.exists(name)
            if args['--json']:
                print(json.dumps({'exists': exists}))
            elif not args['--quiet']:
                print('true' if exists else 'false')
            sys.exit(0 if exists else 1)

        elif cmd == 'clear':
            secrets_obj.clear()
            if not args['--quiet']:
                print('all secrets cleared')

        else:
            finish(True, 'No command specified', __doc__)
    except SecretsKeyMissingException as e:
        finish(True, str(e))
    except DatabaseException as e:
        finish(True, f'Database error: {e}')
    except Exception as e:
        finish(True, f'Error: {e}')
