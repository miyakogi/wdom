#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

from syncer import sync

from wdom.tests.util import TestCase
from wdom.web_node import WebElement


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
        self.assertRegex(self.elm.html, r'<tag id="\d+"></tag>')
        self.assertRegex(self.elm.id, r'\d+')

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
        elm = WebElement('tag', id='myid')
        self.assertEqual('<tag id="myid"></tag>', elm.html)

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
            'insertAdjacentHTML', position='beforeend', html=self.c1.html)

        removed_child1 = self.elm.removeChild(self.c1)
        self.assertIs(removed_child1, self.c1)
        self.assertIsNone(self.c1.parentNode)
        self.assertEqual(self.js_mock.call_count, 2)
        self.js_mock1.assert_not_called()
        self.js_mock.assert_called_with('removeChild', id=self.c1.id)

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
            'insertAdjacentHTML', position='beforebegin', html=self.c2.html)
        self.assertEqual(self.js_mock.call_count, 3)

        with self.assertRaises(ValueError):
            self.elm.removeChild(self.c1)

    def test_addremove_attr(self):
        self.elm.setAttribute('src', 'a')
        self.js_mock.assert_called_with('setAttribute', attr='src', value='a')
        self.elm.removeAttribute('src')
        self.js_mock.assert_called_with('removeAttribute', attr='src')

    def test_set_text_content(self):
        self.elm.textContent = 'text'
        self.js_mock.assert_called_once_with('textContent', text='text')

    def test_set_inner_html(self):
        self.elm.innerHTML = 'html'
        self.js_mock.assert_called_once_with('innerHTML', html='html')

    def test_shallow_copy(self):
        from copy import copy
        clone = copy(self.elm)
        self.assertNotEqual(clone.id, self.elm.id)

        clone = self.elm.cloneNode()
        self.assertNotEqual(clone.id, self.elm.id)

    def test_deep_copy(self):
        from copy import deepcopy
        clone = deepcopy(self.elm)
        self.assertNotEqual(clone.id, self.elm.id)

        clone = self.elm.cloneNode(deep=True)
        self.assertNotEqual(clone.id, self.elm.id)


class TestEventMessage(TestCase):
    def setUp(self):
        self.elm = WebElement('tag')
        self.elm.js_exec = MagicMock()
        self.mock = MagicMock(_is_coroutine=False)
        self.elm.addEventListener('click', self.mock)
        self.msg = {
            'type': 'event',
            'id': self.elm.id,
            'event': {
                'type': 'click',
            },
        }

    def test_handle_event(self):
        self.elm.js_exec.assert_called_once_with('addEventListener', event='click')
        self.elm.on_message(self.msg)
        self.assertTrue(self.mock.called)

    def test_remove_event(self):
        self.elm.removeEventListener('click', self.mock)
        self.elm.js_exec.assert_called_with('removeEventListener', event='click')
        self.elm.on_message(self.msg)
        self.mock.assert_not_called()


class TestQuery(TestCase):
    def setUp(self):
        self._dummy_parent = MagicMock(connected=True, connections=True)
        self.elm = WebElement('tag')
        self.elm._parent = self._dummy_parent
        self.elm.js_exec = MagicMock()
        self.msg = {
            'type': 'response',
            'id': self.elm.id,
        }

    def test_query(self):
        fut = self.elm.js_query('test')
        self.elm.js_exec.assert_called_once_with('test', reqid=0)
        self.msg['reqid'] = 0
        self.msg['data'] = 1
        self.elm._handle_response(self.msg)
        self.assertEqual(fut.result(), 1)

    @sync
    async def test_scroll(self):
        fut = self.elm.scrollX()
        self.assertFalse(fut.done())
        self.msg['reqid'] = 0
        self.msg['data'] = {'x': 1}
        self.elm.on_message(self.msg)
        self.assertEqual(await fut, {'x': 1})
