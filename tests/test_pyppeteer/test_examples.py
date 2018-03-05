#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from syncer import sync

from wdom.util import suppress_logging

from .base import PyppeteerTestCase


def setUpModule():
    suppress_logging()


class TestDataBinding(PyppeteerTestCase):
    def get_elements(self):
        from wdom.examples import data_binding
        root = data_binding.sample_app()
        return root

    @sync
    async def test_app(self):
        h1 = await self.page.J('h1')
        self.assertEqual(await self.get_text(h1), 'Hello!')
        await self.page.type('input', 'abc')
        await self.page.waitForFunction('''
() => document.querySelector("h1").textContent === "abc"
        '''.strip(), timeout=3000)
        self.assertEqual(await self.get_text(h1), 'abc')

        for i in range(3):
            await self.page.keyboard.press('Backspace', {'delay': 10})
        await self.page.waitForFunction('''
() => document.querySelector("h1").textContent === ""
        '''.strip(), timeout=3000)
        self.assertEqual(await self.get_text(h1), '')

        await self.page.type('input', 'new')
        await self.page.waitForFunction('''
() => document.querySelector("h1").textContent === "new"
        '''.strip(), timeout=3000)
        self.assertEqual(await self.get_text(h1), 'new')


class TestGlobalEvent(PyppeteerTestCase):
    def get_elements(self):
        from wdom.examples import global_events
        return global_events.sample_page()

    @sync
    async def test_keypress(self):
        doc_h1 = await self.page.J('#doc1')
        win_h1 = await self.page.J('#win1')
        input_view = await self.page.J('#input_view')
        await self.page.type('#input', 'a')
        await self.page.waitForFunction('''
() => document.querySelector("#input_view").textContent === "a"
        '''.strip(), timeout=3000)
        self.assertEqual(await self.get_text(doc_h1), 'a')
        self.assertEqual(await self.get_text(win_h1), 'a')
        self.assertEqual(await self.get_text(input_view), 'a')

        await self.page.type('#input', 'b')
        await self.page.waitForFunction('''
() => document.querySelector("#input_view").textContent === "b"
        '''.strip(), timeout=3000)
        self.assertEqual(await self.get_text(doc_h1), 'ab')
        self.assertEqual(await self.get_text(win_h1), 'ab')
        self.assertEqual(await self.get_text(input_view), 'b')


class TestRevText(PyppeteerTestCase):
    def get_elements(self):
        from wdom.examples import rev_text
        root = rev_text.sample_app()
        return root

    @sync
    async def test_app(self):
        h1 = await self.page.J('h1')
        text = 'Click!'
        self.assertEqual(await self.get_text(h1), text)

        await h1.click()
        await self.page.waitForFunction('''
() => document.querySelector("h1").textContent === "{}"
        '''.strip().format(text[::-1]), timeout=3000)
        self.assertEqual(await self.get_text(h1), text[::-1])

        await h1.click()
        await self.page.waitForFunction('''
() => document.querySelector("h1").textContent === "{}"
        '''.strip().format(text), timeout=3000)
        self.assertEqual(await self.get_text(h1), text)


class TestTimer(PyppeteerTestCase):
    def get_elements(self):
        from wdom.examples import timer
        return timer.sample_app()

    @sync
    async def test_app(self):
        h1 = await self.page.J('h1')
        start_btn = await self.page.J('#start_btn')
        stop_btn = await self.page.J('#stop_btn')
        reset_btn = await self.page.J('#reset_btn')

        async def test_timer():
            self.assertEqual(await self.get_text(h1), '180.00')
            await start_btn.click()
            await self.wait(0.2)
            self.assertTrue(float(await self.get_text(h1)) < 179.90)
            await stop_btn.click()
            await self.wait(0.1)
            t = await self.get_text(h1)
            await self.wait(0.2)
            self.assertEqual(await self.get_text(h1), t)

        await test_timer()
        await reset_btn.click()
        await self.wait(0.2)
        await test_timer()
