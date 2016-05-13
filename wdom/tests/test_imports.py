#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import subprocess

from nose_parameterized import parameterized

from wdom.testing import TestCase

root = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

cases = [
    ('wdom', 'css'),
    ('wdom', 'document'),
    ('wdom', 'element'),
    ('wdom', 'event'),
    ('wdom', 'interface'),
    ('wdom', 'misc'),
    ('wdom', 'node'),
    ('wdom', 'options'),
    ('wdom', 'parser'),
    ('wdom', 'tag'),
    ('wdom', 'testing'),
    ('wdom', 'web_node'),
    ('wdom', 'webif'),
    ('wdom', 'window'),
    ('wdom', 'server'),
    ('wdom.server', 'base'),
    ('wdom.server', 'handler'),
    ('wdom.server', '_tornado'),
    ('wdom', 'themes'),
    ('wdom.themes', 'default'),
    ('wdom.themes', 'kube'),
    ('wdom.examples', 'data_binding'),
    ('wdom.examples', 'rev_text'),
    ('wdom.examples', 'theming'),
]
try:
    import aiohttp
    cases.append(('wdom.server', '_aiohttp'))
    del aiohttp
except ImportError:
    pass


class TestImportModules(TestCase):
    @parameterized.expand(cases)
    def test_import(self, from_, import_):
        cmd = 'from {0} import {1}\nlist(vars({1}).items())'
        proc = subprocess.Popen(
            [sys.executable, '-c', cmd.format(from_, import_)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=root,
        )
        proc.wait()
        if proc.returncode != 0:
            print(proc.stdout.read())
        self.assertEqual(proc.returncode, 0)

    def test_wdom_import(self):
        cmd = 'import wdom\nlist(vars(wdom).items())'
        proc = subprocess.Popen(
            [sys.executable, '-c', cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=root,
        )
        proc.wait()
        if proc.returncode != 0:
            print(proc.stdout.read())
        self.assertEqual(proc.returncode, 0)
