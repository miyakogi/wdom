#!/usr/bin/env py.test
# -*- coding: utf-8 -*-

import sys
from os import path
import tempfile
from copy import copy
import logging
import unittest
from importlib import reload
import subprocess

import pytest

from wdom.misc import root_dir
from wdom.options import parse_command_line, config, set_loglevel
from wdom import tag
from wdom.themes import default as default_theme

_argv = copy(sys.argv)
_config = copy(vars(config))


def teardown_function(function):
    sys.argv = copy(_argv)
    for k, v in _config.items():
        setattr(config, k, v)


def test_default_loglevel():
    parse_command_line()
    set_loglevel()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.INFO


@pytest.mark.parametrize('level, expected',
                         [('debug', logging.DEBUG),
                          ('info', logging.INFO),
                          ('warn', logging.WARN),
                          ('error', logging.ERROR),
                          ])
def test_loglevel(level, expected):
    sys.argv.extend(['--logging', level])
    parse_command_line()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == expected


def test_debug_without_logging():
    sys.argv.extend(['--debug'])
    parse_command_line()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.DEBUG


def test_debug_with_logging():
    sys.argv.extend(['--debug', '--logging', 'warn'])
    parse_command_line()
    logger = logging.getLogger('wdom')
    assert logger.getEffectiveLevel() == logging.WARN


def test_unknown_args():
    src = '\n'.join([
        'import sys',
        'sys.path.append(\'{}\')'.format(path.dirname(root_dir)),
        'from wdom import options',
    ])
    with tempfile.NamedTemporaryFile('w', dir=path.abspath(path.curdir)) as f:
        f.write(src)
        f.flush()  # save file
        cmd = [sys.executable, f.name, '--test-arg']
        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    assert 'usage: WDOM' in proc.stdout
    assert 'Unknown Argument' in proc.stderr
    assert '--test-arg' in proc.stderr


class TestThemeOption(unittest.TestCase):
    def tearDown(self):
        sys.argv = copy(_argv)
        for k, v in _config.items():
            setattr(config, k, v)

    def test_no_theme(self):
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 1)
        self.assertTrue(log.records[0].msg.startswith('No theme'))
        self.assertTrue(log.records[0].msg.endswith('Use default theme.'))
        self.assertEqual(default_theme.Button, tag.Button)

    def test_bs(self):
        sys.argv.extend(['--theme', 'bootstrap3'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'INFO') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 1)
        self.assertEqual(log.records[0].msg, 'Use theme: bootstrap3')
        from wdom.themes import bootstrap3
        self.assertEqual(default_theme.Button, bootstrap3.Button)

    def test_unknown_theme(self):
        sys.argv.extend(['--theme', 'unknown'])
        parse_command_line()
        with self.assertLogs('wdom.themes', 'WARN') as log:
            reload(default_theme)
        self.assertEqual(len(log.output), 2)
        self.assertTrue(log.records[0].msg.startswith('Unknown theme'))
        self.assertTrue(log.records[1].msg.startswith('Available themes:'))
        self.assertIn('unknown', log.records[0].msg)
        self.assertIn('skeleton', log.records[1].msg)
        self.assertEqual(default_theme.Button, tag.Button)
