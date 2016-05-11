#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase

from wdom.interface import Event, NodeList


class TestEvent(TestCase):
    def setUp(self):
        self.e = Event('event')

    def test_event_type(self):
        self.assertEqual(self.e.type, 'event')


class TestNodeList(TestCase):
    def setUp(self):
        self.nl = NodeList(list(range(3)))

    def test_length(self):
        self.assertEqual(self.nl.length, 3)
        self.assertEqual(len(self.nl), 3)

    def test_index_access(self):
        self.assertEqual(self.nl[1], 1)
        self.assertEqual(self.nl[-1], 2)
        self.assertEqual(self.nl[1:2], [1])
        with self.assertRaises(IndexError):
            self.nl[5]

    def test_item(self):
        self.assertEqual(self.nl.item(1), 1)
        self.assertEqual(self.nl.item(-1), None)
        self.assertEqual(self.nl.item(5), None)
        with self.assertRaises(TypeError):
            self.nl.item(slice(1, 2))

    def test_contains(self):
        self.assertTrue(1 in self.nl)
        self.assertFalse(5 in self.nl)

    def test_iteration(self):
        l = [0, 1, 2]
        for n in self.nl:
            self.assertEqual(n, l.pop(0))
        l = [2, 1, 0]
        for n in reversed(self.nl):
            self.assertEqual(n, l.pop(0))

    def test_index(self):
        self.assertEqual(self.nl.index(0), 0)
        self.assertEqual(self.nl.index(1), 1)
        self.assertEqual(self.nl.index(2), 2)
