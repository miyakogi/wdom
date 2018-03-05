#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from unittest.mock import MagicMock

from syncer import sync

from wdom.node import DocumentFragment, Text
from wdom.web_node import WdomElement
from wdom.util import suppress_logging

from .base import PyppeteerTestCase


def setUpModule():
    suppress_logging()


class TestWdomElement(PyppeteerTestCase):
    def setUp(self):
        super().setUp()

    def get_elements(self):
        root = WdomElement('div')
        self.tag = WdomElement('span', parent=root)
        self.df = DocumentFragment()
        self.c1 = WdomElement('c1')
        self.c2 = WdomElement('c2')
        self.c3 = WdomElement('c3')
        self.c4 = WdomElement('c4')
        self.c1.textContent = 'child1'
        self.c2.textContent = 'child2'
        self.c3.textContent = 'child3'
        self.c4.textContent = 'child4'
        return root

    @sync
    async def test_connection(self):
        self.assertTrue(self.root.connected)
        await self.page.goto('https://example.com')
        await self.wait()
        self.assertFalse(self.root.connected)

    @sync
    async def test_text_content(self):
        self.element = await self.get_element_handle(self.tag)
        self.assertEqual(await self.get_text(), '')
        self.tag.textContent = 'text'
        await self.wait()
        self.assertEqual(await self.get_text(), 'text')

        self.c1.textContent = 'child'
        self.tag.appendChild(self.c1)
        await self.wait_for_element(self.c1)
        self.assertEqual(await self.get_text(), 'textchild')

        self.tag.textContent = 'NewText'
        await self.wait()
        self.assertEqual(await self.get_text(), 'NewText')
        self.assertIsNone(await self.get_element_handle(self.c1))

        t_node = Text('TextNode')
        self.tag.replaceChild(t_node, self.tag.childNodes[0])
        await self.wait()
        self.assertEqual(await self.get_text(), 'TextNode')

        self.tag.removeChild(t_node)
        await self.wait()
        self.assertEqual(await self.get_text(), '')

    @sync
    async def test_attr(self):
        self.element = await self.get_element_handle(self.tag)
        self.assertIsNone(await self.get_attribute('src'))
        self.tag.setAttribute('src', 'a')
        await self.wait()
        self.assertEqual(await self.get_attribute('src'), 'a')
        self.tag.removeAttribute('src')
        await self.wait()
        self.assertIsNone(await self.get_attribute('src'))

    @sync
    async def test_addremove_child(self):
        self.tag.appendChild(self.c1)
        await self.wait_for_element(self.c1)
        self.assertEqual(await self.get_text(), 'child1')
        self.c1.textContent = 'Child'
        await self.wait()
        self.assertEqual(await self.get_text(), 'Child')

        self.tag.removeChild(self.c1)
        await self.wait()
        self.assertIsNone(await self.get_element_handle(self.c1))
        self.assertEqual(await self.get_text(), '')

    @sync
    async def test_insert_child(self):
        # test parent in constructor
        self.c1 = WdomElement('c1', parent=self.tag)
        await self.wait_for_element(self.c1)
        self.c1.textContent = 'child1'

        await self.wait()
        self.assertTrue(await self.get_element_handle(self.c1))
        self.assertIsNone(await self.get_element_handle(self.c2))
        self.assertEqual(await self.get_text(), 'child1')

        self.tag.insertBefore(self.c2, self.c1)
        await self.wait_for_element(self.c2)
        self.assertTrue(await self.get_element_handle(self.c2))
        self.assertEqual(await self.get_text(), 'child2child1')

        self.tag.empty()
        await self.wait()
        self.assertEqual(await self.get_text(), '')
        self.assertIsNone(await self.get_element_handle(self.c1))
        self.assertIsNone(await self.get_element_handle(self.c2))

    @sync
    async def test_add_df(self):
        self.df.append(self.c1, self.c2, 'text')
        self.tag.appendChild(self.df)
        await self.wait_for_element(self.c1)
        await self.wait_for_element(self.c2)
        self.assertEqual(await self.get_text(), 'child1child2text')

        df = DocumentFragment()
        df.append(self.c3, 'text2')
        self.tag.appendChild(df)
        await self.wait_for_element(self.c3)
        self.assertEqual(await self.get_text(), 'child1child2textchild3text2')

    @sync
    async def test_insert_df(self):
        self.tag.appendChild(self.c1)
        await self.wait_for_element(self.c1)
        self.df.append(self.c2, self.c3, 'text')
        self.tag.insertBefore(self.df, self.c1)
        await self.wait_for_element(self.c2)
        await self.wait_for_element(self.c3)
        self.assertEqual(await self.get_text(), 'child2child3textchild1')

        df = DocumentFragment()
        df.append(self.c4, 'text2')
        self.tag.insertBefore(df, self.c3)
        await self.wait_for_element(self.c4)
        self.assertEqual(await self.get_text(), 'child2child4text2child3textchild1')  # noqa

    @sync
    async def test_replace_child(self):
        self.tag.appendChild(self.c1)
        await self.wait_for_element(self.c1)
        self.assertIsNotNone(await self.get_element_handle(self.c1))
        self.assertIsNone(await self.get_element_handle(self.c2))
        self.assertEqual(await self.get_text(), 'child1')

        self.tag.replaceChild(self.c2, self.c1)
        await self.wait_for_element(self.c2)
        self.assertIsNone(await self.get_element_handle(self.c1))
        self.assertIsNotNone(await self.get_element_handle(self.c2))
        self.assertEqual(await self.get_text(), 'child2')

    @sync
    async def test_append(self):
        self.tag.append(self.c1)
        await self.wait_for_element(self.c1)
        self.assertEqual(await self.get_text(), 'child1')

        self.tag.append(self.c2, self.c3)
        await self.wait_for_element(self.c2)
        await self.wait_for_element(self.c3)
        self.assertEqual(await self.get_text(), 'child1child2child3')

        self.tag.append(self.c4, self.c1)
        await self.wait_for_element(self.c4)
        self.assertEqual(await self.get_text(), 'child2child3child4child1')

        self.tag.append('t1', 't2')
        await self.wait()
        self.assertEqual(await self.get_text(), 'child2child3child4child1t1t2')

    @sync
    async def test_prepend(self):
        self.tag.prepend(self.c1)
        await self.wait_for_element(self.c1)
        self.assertEqual(await self.get_text(), 'child1')

        self.tag.prepend(self.c2, self.c3)
        await self.wait_for_element(self.c2)
        await self.wait_for_element(self.c3)
        self.assertEqual(await self.get_text(), 'child2child3child1')

        self.tag.prepend(self.c4, self.c1)
        await self.wait_for_element(self.c4)
        self.assertEqual(await self.get_text(), 'child4child1child2child3')

        self.tag.prepend('t1', 't2')
        await self.wait()
        self.assertEqual(await self.get_text(), 't1t2child4child1child2child3')

    @sync
    async def test_prepend_append_text(self):
        self.tag.append('t1')
        await self.wait()
        self.assertEqual(await self.get_text(), 't1')

        self.tag.firstChild.remove()
        await self.wait()
        self.assertEqual(await self.get_text(), '')

        self.tag.prepend('t2')
        await self.wait()
        self.assertEqual(await self.get_text(), 't2')

        self.tag.append('t3', 't4')
        await self.wait()
        self.assertEqual(await self.get_text(), 't2t3t4')

        self.tag.prepend('t5', 't6')
        await self.wait()
        self.assertEqual(await self.get_text(), 't5t6t2t3t4')

    @sync
    async def test_after(self):
        self.tag.append(self.c1)
        await self.wait_for_element(self.c1)
        self.c1.after(self.c2)
        await self.wait_for_element(self.c2)
        self.assertEqual(await self.get_text(), 'child1child2')

        self.c1.after(self.c3, self.c4)
        await self.wait_for_element(self.c3)
        await self.wait_for_element(self.c4)
        self.assertEqual(await self.get_text(), 'child1child3child4child2')

        self.c1.after(self.c2, 'text')
        await self.wait()
        self.assertEqual(await self.get_text(), 'child1child2textchild3child4')

    @sync
    async def test_before(self):
        self.tag.append(self.c1)
        await self.wait_for_element(self.c1)
        self.c1.before(self.c2)
        await self.wait_for_element(self.c2)
        self.assertEqual(await self.get_text(), 'child2child1')

        self.c1.before(self.c3, self.c4)
        await self.wait_for_element(self.c3)
        await self.wait_for_element(self.c4)
        self.assertEqual(await self.get_text(), 'child2child3child4child1')

        self.c1.before(self.c2, 'text')
        await self.wait()
        self.assertEqual(await self.get_text(), 'child3child4child2textchild1')

    @sync
    async def test_after_before_text(self):
        self.tag.append('a')
        t = self.tag.firstChild
        t.after('b')
        await self.wait()
        self.assertEqual(await self.get_text(), 'ab')

        t.after('c', 'd')
        await self.wait()
        self.assertEqual(await self.get_text(), 'acdb')

        t.before('e')
        await self.wait()
        self.assertEqual(await self.get_text(), 'eacdb')

        t.before('f', 'g')
        await self.wait()
        self.assertEqual(await self.get_text(), 'efgacdb')

    @sync
    async def test_inner_html(self):
        self.tag.innerHTML = '<div>a</div>'
        await self.wait()
        self.assertEqual(await self.get_text(), 'a')

    @sync
    async def test_shortcut_attr(self):
        tag = await self.get_element_handle(self.tag)
        self.tag.textContent = 'TAG'
        await self.wait()
        self.assertFalse(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', tag))
        self.tag.hidden = True
        await self.wait()
        self.assertTrue(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', tag))
        self.tag.hidden = False
        await self.wait()
        self.assertFalse(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', tag))

    @sync
    async def test_style(self):
        self.element = await self.get_element_handle(self.tag)
        self.tag.textContent = 'Style'
        await self.wait()
        self.assertIsNone(await self.get_attribute('style'))
        style = 'color: red;'
        self.tag.style = style
        await self.wait()
        self.assertEqual(await self.get_attribute('style'), style)
        self.tag.style.color = 'black'
        await self.wait()
        self.assertEqual(await self.get_attribute('style'), 'color: black;')

    @sync
    async def test_classlist(self):
        self.element = await self.get_element_handle(self.tag)
        self.assertEqual(await self.get_attribute('class'), None)
        self.assertNotIn(
            'class', await self.page.evaluate('(elm) => elm.outerHTML',
                                              self.element))
        self.tag.classList.add('a')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'a')
        self.tag.classList.add('b', 'c', 'd')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'a b c d')

        self.tag.classList.remove('c')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'a b d')

        self.tag.classList.remove('a', 'd')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'b')

        self.tag.classList.toggle('b')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), None)
        self.assertNotIn(
            'class', await self.page.evaluate('(elm) => elm.outerHTML',
                                              self.element))
        self.tag.classList.toggle('b')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'b')

    @sync
    async def test_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.tag.addEventListener('click', mock)
        self.tag.click()
        await self.wait()
        self.assertEqual(mock.call_count, 1)

    @sync
    async def test_get_rect(self):
        rect = WdomElement('div', style='width:200px;height:100px;')
        self.tag.appendChild(rect)
        await self.wait()

        data = await rect.getBoundingClientRect()
        self.assertEqual(data['width'], 200)
        self.assertEqual(data['height'], 100)

    @sync
    async def test_scroll(self):
        rect = WdomElement('div', style='width:3000px;height:3000px;background:#eee;')  # noqa: #501
        self.tag.appendChild(rect)
        await self.wait()

        X = await rect.scrollX()
        Y = await rect.scrollY()
        self.assertEqual(X['x'], 0)
        self.assertEqual(Y['y'], 0)

        rect.scrollTo(200, 200)
        await asyncio.sleep(self.wait_time)
        X = await rect.scrollX()
        Y = await rect.scrollY()
        self.assertEqual(X['x'], 200)
        self.assertEqual(Y['y'], 200)

    @sync
    async def test_exec(self):
        self.element = await self.get_element_handle(self.tag)
        self.tag.exec('this.style = "color: red;"')
        await self.wait()
        self.assertEqual(await self.get_attribute('style'), 'color: red;')

        self.tag.exec('node.style = "color: blue;"')
        await self.wait()
        self.assertEqual(await self.get_attribute('style'), 'color: blue;')

    @sync
    async def test_exec_error(self):
        with self.assertLogs('wdom.server', 'ERROR') as log:
            self.tag.exec('a.b')
            await self.wait()
        self.assertRegex(log.output[0], r'JS: ReferenceError')


class TestEvent(PyppeteerTestCase):
    def get_elements(self):
        self.root = WdomElement('div')
        self.tag = WdomElement('span', parent=self.root)

        self.click_event_mock = MagicMock()
        self.click_event_mock._is_coroutine = False

        self.btn = WdomElement('button')
        self.btn.textContent = 'click'
        self.btn.addEventListener('click', self.click_event_mock)

        self.input_event_mock = MagicMock()
        self.input_event_mock._is_coroutine = False

        self.input = WdomElement('input', type='text')
        self.input.addEventListener('input', self.input_event_mock)

        self.root.appendChild(self.btn)
        self.root.appendChild(self.input)
        return self.root

    @sync
    async def test_click(self):
        btn = await self.get_element_handle(self.btn)
        await btn.click()
        await self.wait()
        self.assertEqual(self.click_event_mock.call_count, 1)

    @sync
    async def test_input(self):
        await self.page.type(
            '[wdom_id="{}"]'.format(self.input.wdom_id), 'abc')
        await self.wait()
        self.assertEqual(self.input_event_mock.call_count, 3)
