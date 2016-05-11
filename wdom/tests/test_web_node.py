#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from unittest.mock import MagicMock, call

from syncer import sync

from wdom.interface import Event
from wdom.testing import TestCase
from wdom.web_node import WebElement
from wdom.server import set_server_type, _tornado


class TestWebElement(TestCase):
    def setUp(self):
        self.elm = WebElement('tag')
        self.c1 = WebElement()
        self.c2 = WebElement()
        self.js_mock = MagicMock()
        self.js_mock1 = MagicMock()
        self.js_mock2 = MagicMock()
        self.elm.js_exec = self.js_mock
        self.c1.js_exec = self.js_mock1
        self.c2.js_exec = self.js_mock2

    def test_id(self):
        self.assertRegex(self.elm.html, r'<tag rimo_id="\d+"></tag>')
        self.assertRegex(self.elm.rimo_id, r'\d+')

    def test_noid(self):
        self.assertEqual('<tag></tag>', self.elm.html_noid)

        self.c1.tag = 'c1'
        appended_child1 = self.elm.appendChild(self.c1)
        self.assertIs(appended_child1, self.c1)
        self.assertEqual('<tag><c1></c1></tag>', self.elm.html_noid)

        self.c2.tag = 'c2'
        appended_child2 = self.c1.appendChild(self.c2)
        self.assertIs(appended_child2, self.c2)
        self.assertEqual('<tag><c1><c2></c2></c1></tag>', self.elm.html_noid)

    def test_id_init(self):
        elm = WebElement('tag', rimo_id='myid')
        self.assertEqual('<tag rimo_id="myid"></tag>', elm.html)

    def test_not_connected(self):
        self.assertFalse(self.elm.connected)

    def test_parent(self):
        self.assertIsNone(self.elm.parentNode)
        self.assertIsNone(self.c1.parentNode)
        self.elm.appendChild(self.c1)
        self.assertIs(self.elm, self.c1.parentNode)
        self.js_mock1.assert_not_called()
        self.assertEqual(self.js_mock.call_count, 1)
        self.js_mock.assert_called_once_with(
            'insertAdjacentHTML', 'beforeend', self.c1.html)

        removed_child1 = self.elm.removeChild(self.c1)
        self.assertIs(removed_child1, self.c1)
        self.assertIsNone(self.c1.parentNode)
        self.assertEqual(self.js_mock.call_count, 2)
        self.js_mock1.assert_not_called()
        self.js_mock.assert_called_with('removeChildById', self.c1.rimo_id)

    def test_addremove_child(self):
        self.assertFalse(self.elm.hasChildNodes())
        self.elm.appendChild(self.c1)
        self.assertTrue(self.elm.hasChildNodes())
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 1)

        self.elm.insertBefore(self.c2, self.c1)
        self.assertIn(self.c1, self.elm)
        self.assertIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 2)
        self.c2.remove()
        self.assertEqual(self.elm.length, 1)
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertIsNone(self.c2.parentNode)
        self.js_mock2.assert_called_once_with('remove')

        self.elm.removeChild(self.c1)
        self.assertFalse(self.elm.hasChildNodes())
        self.assertEqual(self.elm.length, 0)
        self.assertNotIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.js_mock1.assert_called_once_with(
            'insertAdjacentHTML', 'beforebegin', self.c2.html)
        self.assertEqual(self.js_mock.call_count, 3)

        with self.assertRaises(ValueError):
            self.elm.removeChild(self.c1)

    def test_addremove_attr(self):
        self.elm.setAttribute('src', 'a')
        self.js_mock.assert_called_with('setAttribute', 'src', 'a')
        self.elm.removeAttribute('src')
        self.js_mock.assert_called_with('removeAttribute', 'src')

    def test_style(self):
        self.elm.style = 'color: red;'
        self.js_mock.assert_called_once_with(
            'setAttribute', 'style', 'color: red;')
        self.elm.removeAttribute('style')
        self.js_mock.assert_called_with('removeAttribute', 'style')
        self.elm.style.color = 'black'
        self.js_mock.assert_called_with(
            'setAttribute', 'style', 'color: black;')

    def test_style_init(self):
        _js_exec = WebElement.js_exec
        WebElement.js_exec = self.js_mock
        WebElement('elm', style='color: red;')
        _call = call('setAttribute', 'style', 'color: red;')
        _call_remove = call('removeAttribute', 'style')
        self.js_mock.assert_has_calls([_call])
        count = 0
        for c in self.js_mock.call_args_list:
            if c == _call:
                count += 1
            elif c == _call_remove:
                raise AssertionError('Unexpeted remove style')
        self.assertEqual(count, 1)
        WebElement.js_exec = _js_exec

    def test_set_text_content(self):
        self.elm.textContent = 'text'
        self.js_mock.assert_called_once_with('textContent', 'text')

    def test_set_inner_html(self):
        self.elm.innerHTML = 'html'
        self.js_mock.assert_called_once_with('innerHTML', 'html')

    def test_shallow_copy(self):
        from copy import copy
        clone = copy(self.elm)
        self.assertNotEqual(clone.rimo_id, self.elm.rimo_id)

        clone = self.elm.cloneNode()
        self.assertNotEqual(clone.rimo_id, self.elm.rimo_id)

    def test_deep_copy(self):
        from copy import deepcopy
        clone = deepcopy(self.elm)
        self.assertNotEqual(clone.rimo_id, self.elm.rimo_id)

        clone = self.elm.cloneNode(deep=True)
        self.assertNotEqual(clone.rimo_id, self.elm.rimo_id)

    def test_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.elm.addEventListener('click', mock)
        self.elm.click()
        self.js_mock.assert_called_once_with('addEventListener', 'click')
        self.assertEqual(mock.call_count, 1)


class TestEventMessage(TestCase):
    def setUp(self):
        self.elm = WebElement('tag')
        self.elm.js_exec = MagicMock()
        self.mock = MagicMock(_is_coroutine=False)
        self.elm.addEventListener('click', self.mock)
        self.msg = {
            'type': 'event',
            'id': self.elm.rimo_id,
            'event': {
                'type': 'click',
            },
        }
        self.event = Event(**self.msg.get('event'))

    def test_handle_event(self):
        self.elm.js_exec.assert_called_once_with('addEventListener', 'click')
        self.elm.dispatchEvent(self.event)
        self.assertTrue(self.mock.called)

    def test_remove_event(self):
        self.elm.removeEventListener('click', self.mock)
        self.elm.js_exec.assert_called_with('removeEventListener', 'click')
        self.elm.dispatchEvent(self.event)
        self.mock.assert_not_called()


class TestQuery(TestCase):
    def setUp(self):
        super().setUp()
        set_server_type('tornado')
        _tornado.connections.append(MagicMock())
        self.elm = WebElement('tag')
        self.elm.js_exec = MagicMock()
        self.msg = {
            'type': 'response',
            'id': self.elm.rimo_id,
        }

    def test_query(self):
        fut = self.elm.js_query('test')
        self.elm.js_exec.assert_called_once_with('test', 0)
        self.msg['reqid'] = 0
        self.msg['data'] = 1
        self.elm.on_response(self.msg)
        self.assertEqual(fut.result(), 1)

    @sync
    @asyncio.coroutine
    def test_scroll(self):
        fut = self.elm.scrollX()
        self.assertFalse(fut.done())
        self.msg['reqid'] = 0
        self.msg['data'] = {'x': 1}
        self.elm.on_response(self.msg)
        x = yield from fut
        self.assertEqual(x, {'x': 1})
