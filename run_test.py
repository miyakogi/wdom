#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from wdom.testing import suppress_logging

if __name__ == '__main__':
    suppress_logging()
    tests = unittest.defaultTestLoader.discover('wdom/tests')
    runner = unittest.TextTestRunner()
    runner.run(tests)
