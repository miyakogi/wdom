#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

from syncer import sync

from wdom.tag import Tag, Textarea, Input, Label, Div, Form
from wdom.themes import CheckBox
from wdom.util import suppress_logging

from .base import PyppeteerTestCase


def setUpModule():
    suppress_logging()


class TestTag(PyppeteerTestCase):
    def get_elements(self):
        class Root(Tag):
            tag = 'root'
        return Root()

    def test_connection(self):
        self.assertIsTrue(self.root.connected)
        # this is an example, but valid domain for test
        sync(self.page.goto('http://example.com/'))
        self.assertIsFalse(self.root.connected)

    @sync
    async def test_node_text(self):
        self.assertEqual(await self.get_text(), '')
        self.root.textContent = 'ROOT'
        await self.wait()
        self.assertEqual(await self.get_text(), 'ROOT')

    @sync
    async def test_node_attr(self):
        self.assertIsNone(await self.get_attribute('src'))
        self.root.setAttribute('src', 'a')
        await self.wait()
        self.assertEqual(await self.get_attribute('src'), 'a')
        self.root.removeAttribute('src')
        await self.wait()
        self.assertIsNone(await self.get_attribute('src'))

    @sync
    async def test_node_class(self):
        self.root.addClass('a')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), 'a')
        self.root.removeClass('a')
        await self.wait()
        self.assertEqual(await self.get_attribute('class'), None)
        self.assertNotIn('class',
                         await self.page.evaluate('(elm) => elm.outerHTML',
                                                  self.element))

    @sync
    async def test_addremove_child(self):
        child = Tag()
        self.root.appendChild(child)
        await self.wait()
        self.element = await self.get_element_handle(child)
        self.assertEqual(await self.get_text(), '')
        child.textContent = 'Child'
        await self.wait()
        self.assertEqual(await self.get_text(), 'Child')

        self.root.removeChild(child)
        await self.wait()
        self.assertIsNone(await self.get_element_handle(child))

    @sync
    async def test_replace_child(self):
        child1 = Tag('child1')
        child2 = Tag('child2')
        self.root.appendChild(child1)
        await self.wait()
        self.element = await self.get_element_handle(child1)
        self.assertEqual(await self.get_text(), 'child1')
        self.assertIsNone(await self.get_element_handle(child2))

        self.root.replaceChild(child2, child1)
        await self.wait()
        self.assertIsNone(await self.get_element_handle(child1))
        self.element = await self.get_element_handle(child2)
        self.assertEqual(await self.get_text(), 'child2')

    @sync
    async def test_showhide(self):
        elm = self.element
        self.root.textContent = 'root'
        await self.wait()
        self.assertFalse(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', elm))
        self.root.hide()
        await self.wait()
        self.assertTrue(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', elm))
        self.root.show()
        await self.wait()
        self.assertFalse(
            await self.page.evaluate('(e) => e.hasAttribute("hidden")', elm))


class TestInput(PyppeteerTestCase):
    def get_elements(self):
        self.root = Form()
        self.input = Input(parent=self.root, type='text')
        self.textarea = Textarea(parent=self.root)
        self.checkbox = CheckBox(parent=self.root, id='check1')
        self.check_l = Label('Check 1', parent=self.root, **{'for': 'check1'})
        self.radio1 = Input(parent=self.root, type='radio', name='radio_test', id='r1')  # noqa: E501
        self.radio2 = Input(parent=self.root, type='radio', name='radio_test', id='r2')  # noqa: E501
        self.radio3 = Input(parent=self.root, type='radio', name='radio_test2', id='r3')  # noqa: E501
        self.radio1_l = Label(self.radio1, 'Radio 1', parent=self.root)
        self.radio2_l = Label(self.radio2, 'Radio 2', parent=self.root)
        self.radio3_l = Label(self.radio3, 'Radio 3', parent=self.root)
        return self.root

    @sync
    async def test_textinput(self):
        inputs = []

        def input_handler(e):
            inputs.append(e.data)

        self.input.addEventListener('input', input_handler)
        await self.page.type('[wdom_id="{}"]'.format(self.input.wdom_id), 'a')
        await self.wait()
        self.assertEqual(self.input.value, 'a')
        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0], 'a')

        await self.page.reload()
        self.element = await self.get_element_handle(self.input)
        self.assertEqual(await self.get_attribute('value'), 'a')

        await self.page.type('[wdom_id="{}"]'.format(self.input.wdom_id), 'd')
        await self.wait()
        # focus on top of the text input
        self.assertEqual(self.input.value, 'da')
        self.assertEqual(len(inputs), 2)
        self.assertEqual(inputs[0], 'a')
        self.assertEqual(inputs[1], 'd')

    @sync
    async def test_textarea(self):
        await self.page.type('[wdom_id="{}"]'.format(self.textarea.wdom_id),
                             'abc')
        await self.wait()
        self.element = await self.get_element_handle(self.textarea)
        self.assertEqual(self.textarea.textContent, 'abc')

        await self.page.reload()
        await self.wait()
        self.element = await self.get_element_handle(self.textarea)
        await self.wait()
        self.assertEqual(await self.get_text(), 'abc')

        await self.page.type('[wdom_id="{}"]'.format(self.textarea.wdom_id),
                             'def')
        await self.wait()
        self.assertEqual(self.textarea.textContent, 'defabc')

    @sync
    async def test_checkbox(self):
        self.element = await self.get_element_handle(self.checkbox)
        await self.element.click()
        await self.wait()
        self.assertIsTrue(self.checkbox.checked)

        await self.page.reload()
        await self.wait()
        self.element = await self.get_element_handle(self.checkbox)
        self.assertIsTrue(
            await self.page.evaluate('(e) => e.hasAttribute("checked")',
                                     self.element))

        await self.element.click()
        await self.wait()
        # Error
        # self.assertIsFalse(
        #     await self.element.evaluate('(elm) => elm.hasAttribute("checked")')  # noqa
        # )
        self.assertIsFalse(self.checkbox.checked)

    @sync
    async def test_checkbox_label(self):
        self.element = await self.get_element_handle(self.checkbox)
        await self.element.click()
        await self.wait()
        self.assertTrue(self.checkbox.checked)

        await self.element.click()
        await self.wait()
        self.assertFalse(self.checkbox.checked)

    @sync
    async def test_radios(self):
        self.assertFalse(self.radio1.checked)
        self.assertFalse(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.element = await self.get_element_handle(self.radio1)
        await self.element.click()
        await self.wait()
        self.assertTrue(self.radio1.checked)
        self.assertFalse(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.element = await self.get_element_handle(self.radio2)
        await self.element.click()
        await self.wait()
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)
        self.assertFalse(self.radio3.checked)

        self.element = await self.get_element_handle(self.radio3)
        await self.element.click()
        await self.wait()
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)
        self.assertTrue(self.radio3.checked)

    @sync
    async def test_radios_label(self):
        self.element = await self.get_element_handle(self.radio1_l)
        await self.element.click()
        await self.wait()
        self.assertTrue(self.radio1.checked)
        self.assertFalse(self.radio2.checked)

        self.element = await self.get_element_handle(self.radio2_l)
        await self.element.click()
        await self.wait()
        self.assertFalse(self.radio1.checked)
        self.assertTrue(self.radio2.checked)

    def test_select(self):
        pass

    def test_select_multi(self):
        pass


class TestEvent(PyppeteerTestCase):
    def get_elements(self):
        self.doc.body.style = 'margin: 0; padding: 0;'
        self.elm = Div()
        self.elm.style = '''
            background-color: blue;
            width: 100px;
            height: 100px;
            display: inline-block;
        '''
        self.elm.addEventListener('click', self.click)
        self.test_done = False
        return self.elm

    def click(self, e):
        self.assertFalse(e.altKey)
        self.assertFalse(e.ctrlKey)
        self.assertFalse(e.metaKey)
        self.assertFalse(e.shiftKey)
        self.assertLessEqual(e.clientX, 100)
        self.assertLessEqual(e.clientY, 100)
        self.assertLessEqual(e.offsetX, 100)
        self.assertLessEqual(e.offsetY, 100)
        self.assertLessEqual(e.pageX, 100)
        self.assertLessEqual(e.pageY, 100)
        self.assertLessEqual(e.x, 100)
        self.assertLessEqual(e.y, 100)
        self.test_done = True

    @sync
    async def test_click(self):
        await self.element.click()
        await self.wait()
        self.assertIsTrue(self.test_done)

    @sync
    async def test_document_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.doc.addEventListener('click', mock)
        await self.wait()
        await self.element.click()
        await self.wait()
        self.assertIsTrue(mock.called)

    @sync
    async def test_window_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.doc.defaultView.addEventListener('click', mock)
        await self.wait()
        await self.element.click()
        await self.wait()
        self.assertIsTrue(mock.called)
