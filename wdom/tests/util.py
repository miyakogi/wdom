#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''

'''

import re
import unittest


class TestCase(unittest.TestCase):
    def assertIsTrue(self, bl):
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        self.assertIs(bl, False)

    def assertMatch(self, pattern, string):
        self.assertIsNotNone(re.match(pattern, string))

    def assertNotMatch(self, pattern, string):
        self.assertIsNone(re.match(pattern, string))
        return self.wait_for()
