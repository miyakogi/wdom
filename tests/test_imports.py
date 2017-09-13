#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import subprocess

from parameterized import parameterized

from .base import TestCase

root = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

cases = [
    ('wdom', 'css'),
    ('wdom', 'document'),
    ('wdom', 'element'),
    ('wdom.examples', 'data_binding'),
    ('wdom.examples', 'drag'),
    ('wdom.examples', 'rev_text'),
    ('wdom.examples', 'theming'),
    ('wdom', 'event'),
    ('wdom', 'node'),
    ('wdom', 'options'),
    ('wdom', 'parser'),
    ('wdom', 'server'),
    ('wdom.server', 'base'),
    ('wdom.server', 'handler'),
    ('wdom.server', '_tornado'),
    ('wdom', 'tag'),
    ('wdom', 'themes'),
    ('wdom.themes', 'default'),
    ('wdom.themes', 'bootstrap3'),
    ('wdom', 'util'),
    ('wdom', 'web_node'),
    ('wdom', 'window'),
]


class TestImportModules(TestCase):
    @parameterized.expand(cases)
    def test_import(self, from_, import_):
        cmd = 'from {0} import {1}\nlist(vars({1}).items())'
        proc = subprocess.run(
            [sys.executable, '-c', cmd.format(from_, import_)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=root,
        )
        if proc.returncode != 0:
            print(proc.stdout.read())
        self.assertEqual(proc.returncode, 0)

    def test_wdom_import(self):
        cmd = 'import wdom\nlist(vars(wdom).items())'
        proc = subprocess.run(
            [sys.executable, '-c', cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=root,
        )
        if proc.returncode != 0:
            print(proc.stdout.read())
        self.assertEqual(proc.returncode, 0)
