#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from wdom.util import reset


class TestCase(unittest.TestCase):
    """Base class for testing wdom modules.

    This class is a sub class of the ``unittest.TestCase``. After all test
    methods, reset wdom's global objects like document, application, and
    elements. If you use ``tearDown`` method, do not forget to call
    ``super().tearDown()``.
    """

    def setUp(self) -> None:
        """Reset WDOM states."""
        super().setUp()
        reset()

    def tearDown(self) -> None:
        """Reset WDOM states."""
        reset()
        super().tearDown()

    def assertIsTrue(self, bl: bool) -> None:
        """Check arg is exactly True, not truthy."""
        self.assertIs(bl, True)

    def assertIsFalse(self, bl: bool) -> None:
        """Check arg is exactly False, not falsy."""
        self.assertIs(bl, False)
