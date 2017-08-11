#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from unittest.mock import MagicMock

from wdom.document import get_document
from wdom.server import _tornado
from wdom.server.handler import event_handler
from wdom.testing import TestCase
from wdom.window import customElements


class TestWindow(TestCase):
    def setUp(self):
        super().setUp()
        self.doc = get_document()
        self.win = self.doc.defaultView
        self.conn_mock = MagicMock()
        _tornado.connections.append(self.conn_mock)

    def tearDown(self):
        _tornado.connections.remove(self.conn_mock)

    def test_custom_elements_registory(self):
        self.assertIs(self.win.customElements, customElements)

    def test_document(self):
        self.assertIs(self.win.document, self.doc)
        self.assertIs(self.win, self.doc.defaultView)

    def test_rimo_id(self):
        self.assertEqual(self.win.rimo_id, 'window')

    def test_add_eventlistener(self):
        mock = MagicMock(_is_coroutine=False)
        self.win.js_exec = MagicMock(_is_coroutine=False)
        self.win.addEventListener('click', mock)
        self.win.js_exec.assert_called_once_with('addEventListener', 'click')
        msg = {
            'type': 'click',
            'currentTarget': {'id': 'window'},
            'target': {'id': 'window'},
        }
        e = event_handler(msg)
        mock.assert_called_once_with(e)

    def test_add_event_handler_doc(self):
        mock = MagicMock(_is_coroutine=False)
        self.win.addEventListener('click', mock)
        msg = {
            'type': 'click',
            'currentTarget': {'id': 'document'},
            'target': {'id': 'document'},
        }
        event_handler(msg)
        sleep(0.1)
        mock.assert_not_called()
