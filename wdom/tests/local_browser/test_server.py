#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from os import path
import asyncio
import subprocess
from tempfile import NamedTemporaryFile

from selenium.common.exceptions import NoSuchElementException

from wdom.misc import install_asyncio
from wdom.testing import get_webdriver, free_port, browser_implict_wait
from wdom.testing import TestCase, close_webdriver


def setUpModule():
    install_asyncio()


def tearDownModule():
    close_webdriver()


CURDIR = path.dirname(path.abspath(__file__))

src_base = '''
import sys
import asyncio

from wdom.misc import install_asyncio
from wdom.tag import H1
from wdom.document import get_document
from wdom import server

install_asyncio()
loop = asyncio.get_event_loop()
doc = get_document()
doc.body.appendChild(H1('FIRST', id='h1'))
doc.add_cssfile('testdir/test.css')
server.add_static_path('testdir', '{curdir}/testdir')
server.start_server(loop=loop, check_time=10)
loop.run_forever()
'''.format(curdir=CURDIR)

css_path = path.join(CURDIR, 'testdir/test.css')
src_css = '''
h1 {color: #000000;}
'''
src_css_post = '''
h1 {color: #ff0000;}
'''

_src = src_base.splitlines()
_src.insert(12, 'server.exclude_patterns.append(r\'test.css\')')
src_exclude_css = '\n'.join(_src)
_src = src_base.splitlines()
_src.insert(12, 'server.exclude_patterns.append(r\'testdi*\')')
src_exclude_dir = '\n'.join(_src)


class TestAutoReload(TestCase):
    wait_time = 3 if os.environ.get('TRAVIS') else 1

    @classmethod
    def setUpClass(cls):
        cls.wd = get_webdriver()
        if os.environ.get('TRAVIS', True):
            cls.wd.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if os.environ.get('TRAVIS', True):
            cls.wd.implicitly_wait(browser_implict_wait)

    def setUp(self):
        super().setUp()
        with open(css_path, 'w') as f:
            f.write(src_css)
        self.port = free_port()
        self.url = 'http://localhost:{}'.format(self.port)
        tmpfile = NamedTemporaryFile(mode='w+', dir=CURDIR, suffix='.py',
                                     delete=False)
        self.tmpfilename = tmpfile.name
        tmpfile.close()
        self.proc = None

    def tearDown(self):
        if self.proc is not None and self.proc.returncode is None:
            self.proc.terminate()
        if path.exists(self.tmpfilename):
            os.remove(self.tmpfilename)
        with open(css_path, 'w') as f:
            f.write(src_css)
        super().tearDown()

    def _base_args(self):
        return [sys.executable, self.tmpfilename, '--port', str(self.port),
                '--logging', 'error']

    def wait(self, t: float = None):
        _t = t or self.wait_time
        for i in range(10):
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(_t/10))

    def wait_short(self, t: float = None):
        asyncio.get_event_loop().run_until_complete(
            asyncio.sleep(t or (self.wait_time / 10)))

    def check_reload(self, args):
        self.proc = subprocess.Popen(args, cwd=CURDIR, env=os.environ)
        self.wait()
        self.wd.get(self.url)
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        self.assertEqual(h1.text, 'FIRST')

        with open(self.tmpfilename, 'w') as f:
            f.write(src_base.replace('FIRST', 'SECOND'))
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        h1 = self.wd.find_element_by_id('h1')
        self.assertEqual(h1.text, 'SECOND')

    def test_autoreload(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_base)
        self.wait_short()
        args = self._base_args()
        args.append('--autoreload')
        self.check_reload(args)

    def test_autoreload_debug(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_base)
        self.wait_short()
        args = self._base_args()
        args.append('--debug')
        self.check_reload(args)

    def check_css_reload(self, args):
        self.proc = subprocess.Popen(args, cwd=CURDIR, env=os.environ)
        self.wait()
        self.wd.get(self.url)
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        # value_of_css_property return colors as rgba style
        self.assertRegex(h1.value_of_css_property('color'),
                         r'0,\s*0,\s* 0,\s*1\s*')
        with open(css_path, 'w') as f:
            f.write(src_css_post)
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        self.assertRegex(h1.value_of_css_property('color'),
                         r'255,\s*0,\s* 0,\s*1\s*')

    def test_autoreload_css(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_base)
        self.wait_short()
        args = self._base_args()
        args.append('--autoreload')
        self.check_css_reload(args)

    def check_css_noreload(self, args):
        self.proc = subprocess.Popen(args, cwd=CURDIR, env=os.environ)
        self.wait()
        self.wd.get(self.url)
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        # value_of_css_property return colors as rgba style
        self.assertRegex(h1.value_of_css_property('color'),
                         r'0,\s*0,\s* 0,\s*1\s*')
        with open(css_path, 'w') as f:
            f.write(src_css_post)
        self.wait()
        try:
            h1 = self.wd.find_element_by_id('h1')
        except NoSuchElementException:
            self.wait()
            h1 = self.wd.find_element_by_id('h1')
        self.assertRegex(h1.value_of_css_property('color'),
                         r'0,\s*0,\s* 0,\s*1\s*')

    def test_autoreload_exclude_css(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_exclude_css)
        self.wait_short()
        args = self._base_args()
        args.append('--autoreload')
        self.check_css_noreload(args)

    def test_autoreload_exclude_dir(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_exclude_dir)
        self.wait_short()
        args = self._base_args()
        args.append('--autoreload')
        self.check_css_noreload(args)

    def test_autoreload_nowatch(self):
        with open(self.tmpfilename, 'w') as f:
            f.write(src_base.replace("/testdir'", "/testdir', no_watch=True"))
        self.wait_short()
        args = self._base_args()
        args.append('--autoreload')
        self.check_css_noreload(args)
