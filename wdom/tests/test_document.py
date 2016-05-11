#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from unittest.mock import MagicMock

from wdom import options
from wdom.interface import Event
from wdom.node import DocumentFragment, Comment, Text
from wdom.element import Attr, Element
from wdom.document import Document, get_document, get_new_document, set_document  # noqa
from wdom.document import getElementById, getElementByRimoId
from wdom.web_node import WebElement
from wdom.tag import Tag, HTMLElement, A
from wdom.testing import TestCase


class TestGetElement(TestCase):
    def setUp(self):
        super().setUp()
        Tag._elements_with_id.clear()
        Tag._elements_with_rimo_id.clear()
        self.doc = Document()

    def test_get_element_by_id(self):
        elm = Element(tag='a', id='a')
        self.assertIsNone(getElementById('a'))
        self.doc.appendChild(elm)
        self.assertIs(getElementById('a'), elm)

    def test_get_element_by_rimo_id(self):
        elm = WebElement(tag='a', id='a', rimo_id='b')
        self.assertIsNone(getElementById('a'))
        self.assertIsNone(getElementByRimoId('b'))
        self.doc.appendChild(elm)
        self.assertIs(getElementById('a'), elm)
        self.assertIsNone(getElementByRimoId('a'))
        self.assertIs(getElementByRimoId('b'), elm)


class TestMainDocument(TestCase):
    def setUp(self) -> None:
        super().setUp()
        Tag._elements_with_id.clear()
        Tag._elements_with_rimo_id.clear()
        self.doc = Document()
        self.doc.defaultView.customElements.reset()

    def tearDown(self):
        self.doc.defaultView.customElements.reset()
        super().tearDown()

    def test_blankpage(self) -> None:
        _re = re.compile(
            '\s*<!DOCTYPE html>'
            '\s*<html rimo_id="\d+">'
            '\s*<head rimo_id="\d+">'
            '\s*<meta( charset="utf-8"| rimo_id="\d+"){2}>'
            '\s*<title rimo_id="\d+">'
            '\s*W-DOM'
            '\s*</title>'
            '(\s*<style>.*?</style>)?'
            '\s*</head>'
            '\s*<body rimo_id="\d+">'
            '\s*<script( type="text/javascript"| rimo_id="\d+"){2}>'
            '.*?</script>'
            '\s*</body>'
            '\s*</html>',
            re.S
        )
        html = self.doc.build()
        self.assertIsNotNone(_re.match(html))

    def test_get_element_by_id(self):
        self.assertIsNone(self.doc.getElementById('1'))
        elm = Element('a', parent=self.doc.body, id='a')
        self.assertIs(elm, self.doc.getElementById('a'))
        elm2 = Tag()
        self.assertIsNone(self.doc.getElementByRimoId(elm2.rimo_id))

    def test_get_element_by_remo_id(self):
        self.assertIsNone(self.doc.getElementByRimoId('1'))
        elm = Tag(parent=self.doc.body)
        self.assertIs(elm, self.doc.getElementByRimoId(elm.rimo_id))
        elm2 = Tag()
        self.assertIsNone(self.doc.getElementByRimoId(elm2.rimo_id))

    def test_add_jsfile(self) -> None:
        self.doc.add_jsfile('jsfile')
        _re = re.compile(
            '<body.*'
            '<script( src="jsfile"| type="text/javascript"| rimo_id="\d+"){3}'
            '>\s*</script>'
            '.*</body',
            re.S
        )
        self.assertIsNotNone(_re.search(self.doc.build()))

    def test_add_cssfile(self) -> None:
        self.doc.add_cssfile('cssfile')
        _re = re.compile(
            '<head rimo_id="\d+">.*'
            '<link( href="cssfile"| rel="stylesheet"| rimo_id="\d+"){3}>'
            '.*</head>'
            '', re.S
        )
        self.assertIsNotNone(_re.search(self.doc.build()))

    def test_add_header_link(self) -> None:
        self.doc.add_header('<link href="cssfile" rel="stylesheet">')
        self.assertIn(
            '<link href="cssfile" rel="stylesheet">',
            self.doc.build(),
        )

    def test_add_header_script(self) -> None:
        self.doc.add_header(
            '<script src="jsfile" type="text/javascript"></script>')
        self.assertIn(
            '<script src="jsfile" type="text/javascript"></script>',
            self.doc.build(),
        )

    def test_title(self) -> None:
        doc = Document(title='TEST')
        _re = re.compile(
            '<title rimo_id="\d+">\s*TEST\s*</title>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('W-DOM', html)
        self.assertEqual('TEST', doc.title)

    def test_charset(self) -> None:
        doc = Document(charset='TEST')
        _re = re.compile(
            '<meta( charset="TEST"| rimo_id="\d+"){2}>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('utf', html)
        self.assertEqual('TEST', doc.charset)

    def test_set_body(self) -> None:
        self.doc.body.prepend(Tag())
        html = self.doc.build()
        _re = re.compile(
            '<tag rimo_id="\d+">\s*</tag>',
            re.S
        )
        self.assertIsNotNone(_re.search(html))

    def test_set_body_string(self) -> None:
        string = 'testing'
        self.doc.body.prepend(string)
        html = self.doc.build()
        self.assertIn(string, html)

    def test_set_body_error(self) -> None:
        with self.assertRaises(TypeError):
            self.doc.body.prepend(1)

    def test_create_element(self):
        elm = self.doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, r'<a rimo_id="\d+"></a>')

    def test_create_element_unknown(self):
        elm = self.doc.createElement('aa')
        self.assertEqual(type(elm), HTMLElement)
        self.assertRegex(elm.html, r'<aa rimo_id="\d+"></aa>')

    def test_create_element_defclass(self):
        from wdom import element
        doc = Document(default_class=element.HTMLElement)
        elm = doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a rimo_id="\d+"></a>')

    def test_create_element_defclass_unknown(self):
        from wdom import element
        doc = Document(default_class=element.HTMLElement)
        elm = doc.createElement('aa')
        self.assertEqual(type(elm), element.HTMLElement)
        self.assertRegex(elm.html, '<aa></aa>')

    def test_create_custom_element(self):
        class A(HTMLElement):
            pass
        self.doc.defaultView.customElements.define('a', A)
        elm = self.doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a rimo_id="\d+"></a>')

    def test_create_custom_element_tag(self):
        class A(Tag):
            tag = 'a'
        self.doc.defaultView.customElements.define('a', A)
        elm = self.doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a rimo_id="\d+"></a>')

    def test_create_documentfragment(self):
        df = self.doc.createDocumentFragment()
        self.assertEqual(type(df), DocumentFragment)
        self.assertFalse(df.hasChildNodes())

    def test_create_textnode(self):
        t = self.doc.createTextNode('text')
        self.assertEqual(type(t), Text)
        self.assertEqual(t.html, 'text')

    def test_create_comment(self):
        t = self.doc.createComment('text')
        self.assertEqual(type(t), Comment)
        self.assertEqual(t.html, '<!--text-->')

    def test_create_attr(self):
        a = self.doc.createAttribute('src')
        a.value = 'a'
        self.assertEqual(type(a), Attr)
        self.assertEqual(a.html, 'src="a"')
        tag = HTMLElement('tag')
        tag.setAttributeNode(a)
        self.assertRegex(tag.html, '<tag rimo_id="\d+" src="a"></tag>')

    def test_create_event(self):
        tag = HTMLElement('tag')
        mock = MagicMock(_is_coroutine=False)
        tag.addEventListener('a', mock)
        e = self.doc.createEvent('a')
        self.assertEqual(type(e), Event)
        tag.dispatchEvent(e)
        mock.assert_called_once_with(e)

    def test_custom_tag_theme_tag(self):
        from wdom import tag
        self.doc.register_theme(tag)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, tag.Container))

    def test_custom_tag_theme_default(self):
        from wdom.themes import default
        from wdom import tag
        self.doc.register_theme(default)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, default.Container))
        self.assertTrue(isinstance(elm.firstChild, tag.Container))

    def test_custom_tag_theme(self):
        from wdom.themes import bootstrap3
        from wdom import tag
        self.doc.register_theme(bootstrap3)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.Container))
        self.assertTrue(isinstance(elm.firstChild, tag.Container))
        self.assertIn('maxcdn.bootstrapcdn.com', self.doc.build())

        elm.innerHTML = '<button is="default-button"></button>'
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.DefaultButton))
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.Button))
        self.assertFalse(isinstance(elm.firstChild, tag.DefaultButton))
        self.assertTrue(isinstance(elm.firstChild, tag.Button))

    def test_tempdir(self):
        doc = Document()
        self.assertIsNotNone(doc.tempdir)
        self.assertTrue(os.path.exists(doc.tempdir))
        self.assertTrue(os.path.isabs(doc.tempdir))
        self.assertTrue(os.path.isdir(doc.tempdir))
        tempdir = doc.tempdir
        testfile = os.path.join(tempdir, 'test_file')
        with open(testfile, 'w') as f:
            f.write('test')
        self.assertTrue(os.path.exists(testfile))
        self.assertTrue(os.path.isfile(testfile))
        with open(testfile) as f:
            self.assertEqual('test', f.read().strip())
        del doc
        import gc
        gc.collect()
        self.assertFalse(os.path.exists(testfile))
        self.assertFalse(os.path.exists(tempdir))


class TestDocumentOptions(TestCase):
    def setUp(self):
        super().setUp()
        options.parse_command_line()

    def test_set_new_document(self):
        old_doc = get_document()
        doc = get_new_document()
        self.assertIsNot(doc, old_doc)
        set_document(doc)
        new_doc = get_document()
        self.assertIsNot(doc, old_doc)
        self.assertIs(doc, new_doc)

    def test_document_autoreload(self):
        doc = get_new_document(autoreload=True)
        html = doc.build()
        self.assertIn('RIMO_AUTORELOAD = true', html)
        self.assertNotIn('RIMO_RELOAD_WAIT', html)

    def test_document_reload_wait(self):
        doc = get_new_document(autoreload=True, reload_wait=1234)
        html = doc.build()
        self.assertIn('RIMO_AUTORELOAD = true', html)
        self.assertIn('RIMO_RELOAD_WAIT = 1234', html)

    def test_document_no_reload_wait_no_reload(self):
        doc = get_new_document(autoreload=False, reload_wait=1234)
        html = doc.build()
        self.assertNotIn('RIMO_AUTORELOAD', html)
        self.assertNotIn('RIMO_RELOAD_WAIT', html)

    def test_document_log_level_str(self):
        doc = get_new_document(log_level='INFO')
        html = doc.build()
        self.assertIn('RIMO_LOG_LEVEL = \'INFO\'', html)

    def test_document_log_level_int(self):
        doc = get_new_document(log_level=10)
        html = doc.build()
        self.assertIn('RIMO_LOG_LEVEL = 10', html)

    def test_document_log_prefix(self):
        doc = get_new_document(log_prefix='TEST')
        html = doc.build()
        self.assertIn('RIMO_LOG_PREFIX = \'TEST\'', html)

    def test_document_log_console(self):
        doc = get_new_document(log_console=True)
        html = doc.build()
        self.assertIn('RIMO_LOG_CONSOLE = true', html)

    def test_document_ws_url(self):
        doc = get_new_document(ws_url='test_ws')
        html = doc.build()
        self.assertIn('RIMO_WS_URL = \'test_ws\'', html)
