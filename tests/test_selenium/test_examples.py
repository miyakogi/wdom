#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.color import Color

from wdom.tag import H1
from wdom.document import get_document, set_app
from wdom.util import suppress_logging

from ..base import TestCase
from .base import WebDriverTestCase, close_webdriver


def setUpModule():
    suppress_logging()


def tearDownModule():
    close_webdriver()


class SimpleTestCase(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        document = get_document()
        self.h1 = H1()
        self.h1.textContent = 'TITLE'
        document.body.appendChild(self.h1)
        self.start()

    def test_page(self):
        tag = self.wd.find_element_by_css_selector(
            '[wdom_id="{}"]'.format(self.h1.wdom_id))
        self.assertEqual(tag.text, 'TITLE')


class TestDataBinding(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        from wdom.examples.data_binding import sample_app
        document = get_document()
        document.body.prepend(sample_app())
        self.start()

    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        self.assertEqual(view.text, 'Hello!')
        input = self.wd.find_element_by_tag_name('input')
        self.send_keys(input, 'abcde')
        self.wait_until(lambda: view.text == 'abcde')
        self.assertEqual(view.text, 'abcde')
        for i in range(5):
            self.send_keys(input, Keys.BACKSPACE)
        self.wait_until(lambda: view.text == '')
        self.assertEqual(view.text, '')
        self.send_keys(input, 'new')
        self.wait_until(lambda: view.text == 'new')
        self.assertEqual(view.text, 'new')


class TestDragDrop(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        from wdom.examples.drag import sample_app
        set_app(sample_app())
        self.start()

    def test_app(self):
        elm1 = self.wd.find_element_by_id('1')
        elm2 = self.wd.find_element_by_id('2')
        elm3 = self.wd.find_element_by_id('3')
        self.assertEqual(Color.from_string('red').rgba,
                         elm1.value_of_css_property('background-color'))
        self.assertEqual(Color.from_string('green').rgba,
                         elm2.value_of_css_property('background-color'))
        self.assertEqual(Color.from_string('blue').rgba,
                         elm3.value_of_css_property('background-color'))
        # FIXME: not work selenium's drag/drop
        # from selenium.webdriver import ActionChains
        # from wdom.tests.util import get_webdriver
        # action_chains = ActionChains(get_webdriver())
        # action_chains.drag_and_drop(elm1, elm2).perform()
        # action_chains.click_and_hold(elm1).move_to_element(elm2).release(elm2).perform()
        # self.wait(times=300)
        # self.assertEqual(Color.from_string('green').rgba,
        #                  elm1.value_of_css_property('background-color'))
        # self.assertEqual(Color.from_string('red').rgba,
        #                  elm2.value_of_css_property('background-color'))
        # self.assertEqual(Color.from_string('blue').rgba,
        #                  elm3.value_of_css_property('background-color'))


class TestGlobalEvent(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        from wdom.examples.global_events import sample_page, set_app
        set_app(sample_page())
        self.start()

    def test_keypress(self):
        doc_h1 = self.wd.find_element_by_id('doc1')
        win_h1 = self.wd.find_element_by_id('win1')
        input_view = self.wd.find_element_by_id('input_view')
        input_ = self.wd.find_element_by_id('input')
        input_.send_keys('a')
        self.wait_until(lambda: doc_h1.text == 'a')
        self.wait_until(lambda: win_h1.text == 'a')
        self.wait_until(lambda: input_view.text == 'a')
        self.assertEqual(doc_h1.text, 'a')
        self.assertEqual(win_h1.text, 'a')
        input_.send_keys('b')
        self.wait_until(lambda: doc_h1.text == 'ab')
        self.wait_until(lambda: win_h1.text == 'ab')
        self.wait_until(lambda: input_view.text == 'b')
        self.assertEqual(doc_h1.text, 'ab')
        self.assertEqual(win_h1.text, 'ab')
        self.assertEqual(input_view.text, 'b')


class TestRevText(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        from wdom.examples.rev_text import sample_app
        document = get_document()
        document.body.prepend(sample_app())
        self.start()

    def test_app(self):
        view = self.wd.find_element_by_tag_name('h1')
        text = 'Click!'
        self.assertEqual(view.text, text)
        # need long wait time
        self.wait(times=20)
        view.click()
        self.wait(times=20)
        self.wait_until(lambda: view.text == text[::-1])
        self.assertEqual(view.text, text[::-1])
        self.wait(times=20)
        view.click()
        self.wait(times=20)
        self.wait_until(lambda: view.text == text)
        self.assertEqual(view.text, text)


class TestTimer(WebDriverTestCase, TestCase):
    def setUp(self):
        super().setUp()
        from wdom.examples.timer import sample_app
        document = get_document()
        document.body.prepend(sample_app())
        self.start()

    def test_timer(self):
        view = self.wd.find_element_by_tag_name('h1')
        start_btn = self.wd.find_element_by_id('start_btn')
        stop_btn = self.wd.find_element_by_id('stop_btn')
        reset_btn = self.wd.find_element_by_id('reset_btn')
        self.wait(times=20)

        def test_timer():
            self.assertEqual(view.text, '180.00')
            start_btn.click()
            self.wait(times=20)
            self.assertTrue(float(view.text) < 179.90)
            stop_btn.click()
            self.wait(times=20)
            t = view.text
            self.wait(times=20)
            self.assertEqual(view.text, t)

        test_timer()
        self.wait(times=20)
        reset_btn.click()
        self.wait(times=20)
        test_timer()
