#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Utitlity TesCase
'''

import unittest


class TestCase(unittest.TestCase):
    def assertIsTrue(self, bl):
        self.assertIs(bl, True)

    def assertIsFalse(self, bl):
        self.assertIs(bl, False)
