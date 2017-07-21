#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import unittest
from wdom.testing import suppress_logging


def main():
    suppress_logging()
    target_dir = path.dirname(__file__)
    tests = unittest.defaultTestLoader.discover(target_dir)
    runner = unittest.TextTestRunner()
    runner.run(tests)


if __name__ == '__main__':
    main()
