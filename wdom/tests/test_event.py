#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from unittest.mock import MagicMock, call

from syncer import sync

from wdom.document import get_document
from wdom.event import Event, EventListener, EventTarget, create_event
from wdom.web_node import WdomElement
from wdom.server.handler import create_event_from_msg
from wdom.testing import TestCase


class TestEvent(TestCase):
    def setUp(self):
        self.msg = {}
        self.e = Event('event', init=self.msg)

    def test_event(self):
        self.assertEqual(self.e.type, 'event')
        self.assertIs(self.e.init, self.msg)
        self.assertIsNone(self.e.currentTarget)
        self.assertIsNone(self.e.target)

    def test_craete_event(self):
        self.elm = WdomElement('tag')
        msg = {}
        e = create_event('event', currentTarget=self.elm, target=self.elm,
                         init=msg)
        self.assertEqual(e.type, 'event')
        self.assertIs(e.currentTarget, self.elm)
        self.assertIs(e.target, self.elm)
        self.assertIs(e.init, msg)


class TestCreateEventMsg(TestCase):
    def setUp(self):
        self.elm = WdomElement('tag')
        self.doc = get_document()

    def test_event_from_msg(self):
        msg = {
            'type': 'event',
            'currentTarget': {'id': self.elm.rimo_id},
            'target': {'id': self.elm.rimo_id},
        }
        e = create_event_from_msg(msg)
        self.assertEqual(e.type, 'event')
        self.assertIs(e.currentTarget, self.elm)
        self.assertIs(e.target, self.elm)
        self.assertIs(e.init, msg)

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
        self.assertEqual(len(self.target._listeners), 1)
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
        self.assertEqual(len(self.target._listeners), 2)
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
        self.assertEqual(len(self.target._listeners), 1)
        self.target.removeEventListener('click', self.mock)
        self.assertEqual(len(self.target._listeners), 0)
        self.target.dispatchEvent(self.e)
        self.mock.assert_not_called()
