#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from copy import deepcopy
from unittest.mock import MagicMock, call

from syncer import sync

from wdom.document import get_document
from wdom.event import Event, EventListener, EventTarget, create_event
from wdom.event import MouseEvent, DataTransfer, DragEvent
from wdom.server.handler import create_event_from_msg
from wdom.web_node import WdomElement

from .base import TestCase


class TestDataTransfer(TestCase):
    def test_empty(self):
        dt = DataTransfer()
        self.assertEqual(dt.length, 0)
        self.assertEqual(dt.getData('test'), '')

    def test_set_clear_data(self):
        dt = DataTransfer()
        dt.setData('text/plain', 'test')
        self.assertEqual(dt.getData('text/plain'), 'test')
        self.assertEqual(dt.getData('test'), '')
        dt.setData('text/plain', 'test2')
        self.assertEqual(dt.getData('text/plain'), 'test2')
        dt.setData('text/html', 'test3')
        self.assertEqual(dt.getData('text/plain'), 'test2')
        self.assertEqual(dt.getData('text/html'), 'test3')
        dt.clearData('text/plain')
        self.assertEqual(dt.getData('text/plain'), '')
        self.assertEqual(dt.getData('text/html'), 'test3')
        dt.clearData()
        self.assertEqual(dt.getData('text/plain'), '')
        self.assertEqual(dt.getData('text/html'), '')

    def test_normalize(self):
        dt = DataTransfer()
        dt.setData('text', 'test')
        self.assertEqual(dt.getData('text'), 'test')
        self.assertEqual(dt.getData('text/plain'), 'test')
        self.assertEqual(dt.getData('text/html'), '')

        dt.clearData('text')
        self.assertEqual(dt.getData('text'), '')
        self.assertEqual(dt.getData('text/plain'), '')
        self.assertEqual(dt.getData('text/html'), '')


class TestEvent(TestCase):
    def setUp(self):
        self.msg = {'type': 'event'}
        self.e = Event('event', init=self.msg)

    def test_event(self):
        self.assertEqual(self.e.type, 'event')
        self.assertIs(self.e.init, self.msg)
        self.assertIsNone(self.e.currentTarget)
        self.assertIsNone(self.e.target)

    def test_craete_event(self):
        self.elm = WdomElement('tag')
        msg = {
            'proto': 'event',
            'type': 'event',
            'currentTarget': {'id': self.elm.wdom_id},
            'target': {'id': self.elm.wdom_id},
        }
        e = create_event(msg)
        self.assertEqual(e.type, 'event')
        self.assertIs(e.currentTarget, self.elm)
        self.assertIs(e.target, self.elm)
        self.assertIs(e.init, msg)


class TestDragEvent(TestCase):
    def setUp(self):
        super().setUp()
        self.msg = {
            'type': 'drag',
            'proto': 'DragEvent',
            'dataTransfer': {'id': ''},
        }
        self.msg1 = deepcopy(self.msg)
        self.msg2 = deepcopy(self.msg)
        self.msg3 = deepcopy(self.msg)
        self.msg4 = deepcopy(self.msg)
        self.msg5 = deepcopy(self.msg)
        self.msg1['type'] = 'dragstart'
        self.msg2['type'] = 'dragend'
        self.msg3['type'] = 'drop'
        self.msg4['type'] = 'dragstart'
        self.msg5['type'] = 'drop'
        self.msg1['dataTransfer']['id'] = '1'
        self.msg2['dataTransfer']['id'] = '1'
        self.msg3['dataTransfer']['id'] = '1'
        self.msg4['dataTransfer']['id'] = '2'
        self.msg5['dataTransfer']['id'] = '2'

    def tearDown(self):
        DataTransfer._store.clear()
        super().tearDown()

    def test_init(self):
        de = DragEvent('drag', self.msg)
        self.assertEqual(de.type, 'drag')
        self.assertEqual(de.dataTransfer.getData('test'), '')

    def test_start_drop_end(self):
        de1 = DragEvent('dragstart', self.msg1)
        self.assertEqual(len(DataTransfer._store), 1)
        de1.dataTransfer.setData('text/plain', 'test')
        self.assertEqual(de1.dataTransfer.getData('text/plain'), 'test')

        de3 = DragEvent('drop', self.msg3)
        self.assertEqual(len(DataTransfer._store), 1)
        self.assertEqual(de3.dataTransfer.getData('text/plain'), 'test')

        de2 = DragEvent('dragend', self.msg2)
        self.assertEqual(len(DataTransfer._store), 0)
        self.assertEqual(de2.dataTransfer.getData('text/plain'), 'test')

    def test_different_id(self):
        de1 = DragEvent('dragstart', self.msg1)  # id = 1
        self.assertEqual(len(DataTransfer._store), 1)
        de1.dataTransfer.setData('text/plain', 'test')

        de2 = DragEvent('drop', self.msg5)  # id = 2
        self.assertEqual(len(DataTransfer._store), 2)
        self.assertEqual(de2.dataTransfer.getData('text/plain'), '')

        de3 = DragEvent('drop', self.msg3)  # id = 1
        self.assertEqual(len(DataTransfer._store), 2)
        self.assertEqual(de3.dataTransfer.getData('text/plain'), 'test')


class TestCreateEventMsg(TestCase):
    def setUp(self):
        self.elm = WdomElement('tag')
        self.doc = get_document()

    def test_event_from_msg(self):
        msg = {
            'type': 'event',
            'currentTarget': {'id': self.elm.wdom_id},
            'target': {'id': self.elm.wdom_id},
        }
        e = create_event_from_msg(msg)
        self.assertEqual(e.type, 'event')
        self.assertIs(e.currentTarget, self.elm)
        self.assertIs(e.target, self.elm)
        self.assertIs(e.init, msg)
        self.assertTrue(isinstance(e, Event))

    def test_event_from_msg_proto(self):
        msg = {
            'proto': 'MouseEvent',
            'type': 'event',
            'currentTarget': {'id': self.elm.wdom_id},
            'target': {'id': self.elm.wdom_id},
        }
        e = create_event_from_msg(msg)
        self.assertEqual(e.type, 'event')
        self.assertIs(e.currentTarget, self.elm)
        self.assertIs(e.target, self.elm)
        self.assertIs(e.init, msg)
        self.assertTrue(isinstance(e, Event))
        self.assertTrue(isinstance(e, MouseEvent))

    def test_event_from_msg_notarget(self):
        msg = {
            'type': 'event',
        }
        e = create_event_from_msg(msg)
        self.assertEqual(e.type, 'event')
        self.assertIsNone(e.currentTarget)
        self.assertIsNone(e.target)
        self.assertIs(e.init, msg)


class TestEventListener(TestCase):
    def setUp(self):
        self._cofunc_call_count = 0
        self._cofunc_calls = []

        async def a(event):
            nonlocal self
            self._cofunc_call_count += 1
            self._cofunc_calls.append(event)
            await asyncio.sleep(0)

        self.e = Event('event')
        self.func = MagicMock(_is_coroutine=False)
        self.cofunc = a
        self.func_listener = EventListener(self.func)
        self.cofunc_listener = EventListener(self.cofunc)

    def test_func(self):
        self.func_listener(self.e)
        self.func.assert_called_once_with(self.e)

    @sync
    async def test_cofunc(self):
        await self.cofunc_listener(self.e)
        self.assertEqual(self._cofunc_call_count, 1)
        self.assertEqual(self._cofunc_calls[0], self.e)


class TestEventTarget(TestCase):
    def setUp(self):
        self.target = EventTarget()
        self.mock = MagicMock(_is_coroutine=False)
        self.e = Event('click')

    def test_event_dispatch(self):
        self.target.addEventListener('click', self.mock)
        self.assertEqual(len(self.target._event_listeners), 1)
        self.target.dispatchEvent(self.e)
        self.mock.assert_called_once_with(self.e)

    def test_event_dispatch_empty(self):
        self.target.dispatchEvent(self.e)
        self.mock.assert_not_called()

    def test_event_dispatch_multi(self):
        e1 = Event('click')
        e2 = Event('click')
        self.target.addEventListener('click', self.mock)
        self.target.dispatchEvent(e1)
        self.target.dispatchEvent(e2)
        self.assertEqual(self.mock.call_count, 2)
        self.mock.assert_has_calls([call(e1), call(e2)])

    def test_defferent_event_dispatch(self):
        mock1 = MagicMock(_is_coroutine=False)
        mock2 = MagicMock(_is_coroutine=False)
        e1 = Event('click')
        e2 = Event('event')
        self.target.addEventListener('click', mock1)
        self.target.addEventListener('event', mock2)
        self.assertEqual(len(self.target._event_listeners), 2)
        self.target.dispatchEvent(e1)
        mock1.assert_called_once_with(e1)
        mock2.assert_not_called()

        self.target.dispatchEvent(e2)
        mock1.assert_called_once_with(e1)
        mock2.assert_called_once_with(e2)

    def test_remove_event(self):
        self.target.addEventListener('click', self.mock)
        self.target.removeEventListener('click', self.mock)
        self.target.dispatchEvent(self.e)
        self.mock.assert_not_called()

    def test_remove_event_multi(self):
        self.target.addEventListener('click', self.mock)
        self.assertEqual(len(self.target._event_listeners), 1)
        self.target.removeEventListener('click', self.mock)
        self.assertEqual(len(self.target._event_listeners), 0)
        self.target.dispatchEvent(self.e)
        self.mock.assert_not_called()
