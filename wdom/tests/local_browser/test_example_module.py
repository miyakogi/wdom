#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import time
import unittest

from selenium.webdriver.common.utils import free_port

from wdom.testing import TestCase
from wdom.testing import close_webdriver, get_webdriver


@unittest.skipIf(os.environ.get('TRAVIS', False), reason='skip on CI')
def setUpModule():
    pass


def tearDownModule():
    close_webdriver()


class BaseTestCase(object):
    module = ''

    def setUp(self):
        self.wd = get_webdriver()
        self.port = free_port()
        cmd = [sys.executable, '-m', self.module, '--port', str(self.port)]
        self.proc = subprocess.Popen(cmd, env=os.environ,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     )
        self.url = 'http://localhost:{}'.format(self.port)
        time.sleep(0.5)
        self.wd.get(self.url)

    def tearDown(self):
        self.proc.terminate()
        super().tearDown()


class TestReverseText(BaseTestCase, TestCase):
    module = 'wdom.examples.rev_text'

    def test_revtext(self):
        text = 'Click!'
        h1 = self.wd.find_element_by_tag_name('h1')
        self.assertEqual(h1.text, text)
        time.sleep(0.5)
        h1.click()
        time.sleep(0.5)
        self.assertEqual(h1.text, text[::-1])
        h1.click()
        time.sleep(0.5)
        self.assertEqual(h1.text, text)


class TestDataBinding(BaseTestCase, TestCase):
    module = 'wdom.examples.data_binding'

    def test_revtext(self):
        h1 = self.wd.find_element_by_tag_name('h1')
        input = self.wd.find_element_by_tag_name('input')
        time.sleep(0.5)
        for k in 'test':
            input.send_keys(k)
        time.sleep(0.5)
        self.assertEqual(h1.text, 'test')


class TestTimer(BaseTestCase, TestCase):
    module = 'wdom.examples.timer'

    def test_timer(self):
        view = self.wd.find_element_by_tag_name('h1')
        start_btn = self.wd.find_element_by_id('start_btn')
        stop_btn = self.wd.find_element_by_id('stop_btn')
        reset_btn = self.wd.find_element_by_id('reset_btn')
        time.sleep(0.5)

        def test_timer():
            self.assertEqual(view.text, '180.00')
            start_btn.click()
            time.sleep(0.5)
            self.assertTrue(float(view.text) < 179.90)
            stop_btn.click()
            t = view.text
            time.sleep(0.5)
            self.assertEqual(view.text, t)

        test_timer()
        reset_btn.click()
        time.sleep(0.5)
        test_timer()
