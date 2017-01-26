# -*- coding: utf-8 -*-

"""
    zoom.request

    Web requsets.
"""

import os
import sys
import cgi
import json
import uuid
from timeit import default_timer as timer

from zoom.cookies import (
    get_cookies,
    SESSION_COOKIE_NAME,
    SUBJECT_COOKIE_NAME,
)


class Webvars(object):
    """Extracts parameters sent as part of the request"""

    # pylint: disable=too-few-public-methods

    def __init__(self, env=None, body=None):
        """gather query fields"""

        env = env or os.environ
        get = env.get

        # switch to binary mode on windows systems
        # msvcrt and O_BINARY are only defined in Windows Python
        # pylint: disable=import-error
        # pylint: disable=no-member
        try:
            import msvcrt
            msvcrt.setmode(0, os.O_BINARY)  # stdin  = 0
            msvcrt.setmode(1, os.O_BINARY)  # stdout = 1
        except ImportError:
            pass

        module = get('wsgi.version', None) and 'wsgi' or 'cgi'

        if get('REQUEST_METHOD', 'GET').upper() in ['GET']:
            cgi_fields = cgi.FieldStorage(environ=env, keep_blank_values=1)
        else:
            if module == 'wsgi':
                body_stream = body
                post_env = env.copy()
                post_env['QUERY_STRING'] = ''
            else:
                body_stream = body
                post_env = env.copy()

            cgi_fields = cgi.FieldStorage(
                fp=body_stream,
                environ=post_env,
                keep_blank_values=True
            )

        items = {}
        for key in cgi_fields.keys():

            if isinstance(cgi_fields[key], list):
                items[key] = [item.value for item in cgi_fields[key]]
            elif cgi_fields[key].filename:
                items[key] = cgi_fields[key]
            else:
                items[key] = cgi_fields[key].value
        self.__dict__.update(items)

    def __getattr__(self, name):
        return ''  # return blank for missing attributes

    def __str__(self):
        return repr(self.__dict__)

    def __repr__(self):
        return str(self)


def get_web_vars(env, body):
    """return web parameters as a dict"""
    return Webvars(env, body).__dict__


def get_parent_dir():
    """get the directory above the current directory"""
    return os.path.split(os.path.abspath(os.getcwd()))[0]


class Request(object):
    """A web request"""

    # pylint: disable=too-few-public-methods, too-many-instance-attributes

    def __init__(self, env=None, instance=None, start_time=None):
        self.env = env or os.environ
        self.start_time = start_time or timer()
        self.ip_address = None
        self.session_token = None
        self.server = None
        self.route = []
        self.setup(self.env, instance)
        self.body_consumed = False

    @property
    def body(self):
        """access the body in raw form"""
        self.body_consumed = True
        return self._body

    @property
    def data(self):
        """access the body as data"""
        if not self.body_consumed:
            return get_web_vars(self.env, self._body)
        else:
            return {}

    @property
    def json_body(self):
        """access and parse the body as json"""
        return json.loads(self.body.read().decode('utf-8'))

    def setup(self, env, instance=None):
        """setup the Request attributes"""

        def new_subject():
            """generate a new subject ID"""
            return uuid.uuid4().hex

        def calc_domain(host):
            """calculate just the high level domain part of the host name

            remove the port and the www. if it exists

            >>> calc_domain('www.dsilabs.ca:8000')
            'dsilabs.ca'

            >>> calc_domain('test.dsilabs.ca:8000')
            'test.dsilabs.ca'

            """
            if host:
                return host.split(':')[0].split('www.')[-1:][0]
            return ''

        get = env.get

        self._body = None
        self.body_consumed = False

        path = get('PATH_INFO', get('REQUEST_URI', '').split('?')[0])

        module = get('wsgi.version', None) and 'wsgi' or 'cgi'
        if module == 'wsgi':
            self.server = (get('HTTP_HOST') or '').split(':')[0]
            self.home = os.getcwd()
            self._body = get('wsgi.input')
            self.wsgi_version = get('wsgi.version')
            self.wsgi_urlscheme = get('wsgi.urlscheme')
            self.wsgi_multiprocess = get('wsgi.multiprocess')
            self.wsgi_multithread = get('wsgi.multithread')
            self.wsgi_filewrapper = get('wsgi.filewrapper')
            self.wsgi_runonce = get('wsgi.runonce')
            self.wsgi_errors = get('wsgi.errors')
            self.wsgi_input = get('wsgi.input')
            self.mode = get('mod_wsgi.process_group', None) \
                and 'daemon' or 'embedded'
        else:
            self.server = get('SERVER_NAME', 'localhost')
            self.home = os.path.dirname(get('SCRIPT_FILENAME', ''))
            self._body = sys.stdin

        self.path = path
        self.instance = instance or get_parent_dir()
        self.root = os.path.join(self.instance, 'sites', self.server)
        self.host = get('HTTP_HOST')
        self.domain = calc_domain(get('HTTP_HOST'))
        self.uri = get('REQUEST_URI', 'index.py')
        self.query = get('QUERY_STRING')
        self.ip_address = get('REMOTE_ADDR')
        self.user = get('REMOTE_USER')
        self.cookies = get_cookies(get('HTTP_COOKIE'))
        self.session_token = self.cookies.get(SESSION_COOKIE_NAME, None)
        self.subject = self.cookies.get(SUBJECT_COOKIE_NAME, new_subject())
        self.port = get('SERVER_PORT')
        self.script = get('SCRIPT_FILENAME')
        self.agent = get('HTTP_USER_AGENT')
        self.method = get('REQUEST_METHOD')
        self.module = module
        self.protocol = get('HTTPS', 'off') == 'on' and 'https' or 'http'
        self.referrer = get('HTTP_REFERER')
        self.route = path != '/' and path.split('/')[1:] or []
        self.env = env

    def __str__(self):
        return '{\n%s\n}' % '\n'.join(
            '  %s: %r' % (
                key,
                self.__dict__[key]
            ) for key in self.__dict__
        )
