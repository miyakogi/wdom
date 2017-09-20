#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from unittest.mock import MagicMock

from wdom import options, server
from wdom.document import Document, WdomDocument
from wdom.document import get_document, get_new_document, set_document
from wdom.document import getElementById, getElementByWdomId
from wdom.element import Attr, Element
from wdom.event import Event
from wdom.node import DocumentFragment, Comment, Text
from wdom.server.handler import event_handler
from wdom.tag import Tag, A
from wdom.web_node import WdomElement, remove_wdom_id

from .base import TestCase


class TestGetElement(TestCase):
    def setUp(self):
        super().setUp()
        self.doc = WdomDocument()

    def test_get_element_by_id(self):
        elm = Element(tag='a', id='a')
        self.assertIs(getElementById('a'), elm)
        self.assertIsNone(self.doc.getElementById('a'), elm)
        self.doc.appendChild(elm)
        self.assertIs(getElementById('a'), elm)

    def test_get_element_by_wdom_id(self):
        elm = WdomElement(tag='a')
        wdom_id = elm.wdom_id
        self.assertIs(getElementByWdomId(wdom_id), elm)
        self.assertIsNone(self.doc.getElementByWdomId(wdom_id))
        self.doc.appendChild(elm)
        self.assertIs(getElementByWdomId(wdom_id), elm)
        self.assertIs(self.doc.getElementByWdomId(wdom_id), elm)

    def test_get_element_by_wdom_id_doc(self):
        doc = getElementByWdomId('document')
        self.assertIs(get_document(), doc)

    def test_get_element_by_wdom_id_win(self):
        win = getElementByWdomId('window')
        self.assertIs(get_document().defaultView, win)


class TestDocument(TestCase):
    def setUp(self):
        super().setUp()
        self.doc = Document()

    def test_doctype(self):
        from wdom.node import DocumentType
        self.assertTrue(isinstance(self.doc.doctype, DocumentType))
        self.assertEqual(self.doc.doctype.html, '<!DOCTYPE html>')

    def test_html(self):
        from wdom.tag import Html
        self.assertTrue(isinstance(self.doc.documentElement, Html))
        # html element has <head> and <body>
        self.assertEqual(self.doc.documentElement.length, 2)

    def test_head(self):
        from wdom.tag import Head
        self.assertTrue(isinstance(self.doc.head, Head))
        self.assertEqual(self.doc.head.length, 0)  # head is empty

    def test_body(self):
        from wdom.tag import Body
        self.assertTrue(isinstance(self.doc.body, Body))
        self.assertEqual(self.doc.body.length, 0)  # body is empty

    def test_charset(self):
        # head element is empty
        self.assertEqual(self.doc.head.length, 0)
        self.assertEqual(self.doc.characterSet, '')
        # head element is still empty
        self.assertEqual(self.doc.head.length, 0)
        self.doc.characterSet = 'utf-8'
        self.assertEqual(self.doc.characterSet, 'utf-8')
        # head element has <meta charset="utf-8"> now
        self.assertEqual(self.doc.head.length, 1)

    def test_title(self):
        # head element is empty
        self.assertEqual(self.doc.head.length, 0)
        self.assertEqual(self.doc.title, '')
        # head element is still empty
        self.assertEqual(self.doc.head.length, 0)
        self.doc.title = 'test wdom'
        self.assertEqual(self.doc.title, 'test wdom')
        # head element has <title> now
        self.assertEqual(self.doc.head.length, 1)

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
        tag = Element('tag')
        tag.setAttributeNode(a)
        self.assertEqual(tag.html, '<tag src="a"></tag>')

    def test_create_event(self):
        tag = WdomElement('tag')
        mock = MagicMock(_is_coroutine=False)
        tag.addEventListener('a', mock)
        e = self.doc.createEvent('a')
        self.assertEqual(type(e), Event)
        tag.dispatchEvent(e)
        mock.assert_called_once_with(e)

    def test_add_eventlistener(self):
        mock = MagicMock(_is_coroutine=False)
        self.doc.addEventListener('click', mock)
        msg = {
            'type': 'click',
            'currentTarget': {'id': 'document'},
            'target': {'id': 'document'},
        }
        e = Event('click', msg)
        self.doc.dispatchEvent(e)
        mock.assert_called_once_with(e)

    def test_query_selector(self):
        with self.assertRaises(NotImplementedError):
            self.doc.querySelector('tag')

    def test_query_selector_all(self):
        with self.assertRaises(NotImplementedError):
            self.doc.querySelectorAll('tag')


class TestWdomDocument(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.doc = WdomDocument()
        self.doc.defaultView.customElements.reset()
        server._tornado.connections = [1]

    def test_blankpage(self) -> None:
        _re = re.compile(
            '\s*<!DOCTYPE html>'
            '\s*<html>'
            '\s*<head>'
            '\s*<meta charset="utf-8">'
            '\s*<title>'
            '\s*W-DOM'
            '\s*</title>'
            '(\s*<script type="text/javascript">.*?</script>)?'
            '\s*</head>'
            '\s*<body>'
            '\s*<script type="text/javascript">'
            '.*?</script>'
            '\s*</body>'
            '.*</html>',
            re.S
        )
        html = self.doc.build()
        self.assertIsNotNone(_re.match(remove_wdom_id(html)))

    def test_get_element_by_id(self):
        elm = WdomElement(tag='a', id='a', wdom_id='b')
        self.assertIs(getElementById('a'), elm)
        self.assertIs(getElementByWdomId('b'), elm)
        self.assertIsNone(self.doc.getElementById('a'))
        self.assertIsNone(self.doc.getElementByWdomId('b'), elm)

        self.doc.appendChild(elm)
        self.assertIs(getElementById('a'), elm)
        self.assertIs(getElementByWdomId('b'), elm)
        self.assertIs(self.doc.getElementById('a'), elm)
        self.assertIs(self.doc.getElementByWdomId('b'), elm)

    def test_add_jsfile(self) -> None:
        self.doc.add_jsfile('jsfile')
        _re = re.compile(
            '<body.*'
            '<script( src="jsfile"| type="text/javascript"| wdom_id="\d+"){3}'
            '>\s*</script>'
            '.*</body',
            re.S
        )
        self.assertIsNotNone(_re.search(self.doc.build()))

    def test_add_cssfile(self) -> None:
        self.doc.add_cssfile('cssfile')
        _re = re.compile(
            '<head wdom_id="\d+">.*'
            '<link( href="cssfile"| rel="stylesheet"| wdom_id="\d+"){3}>'
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
        doc = WdomDocument(title='TEST')
        _re = re.compile(
            '<title wdom_id="\d+">\s*TEST\s*</title>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('W-DOM', html)
        self.assertEqual('TEST', doc.title)

    def test_charset(self) -> None:
        doc = WdomDocument(charset='TEST')
        _re = re.compile(
            '<meta( charset="TEST"| wdom_id="\d+"){2}>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('utf', html)
        self.assertEqual('TEST', doc.characterSet)

    def test_set_body(self) -> None:
        self.doc.body.prepend(Tag())
        html = self.doc.build()
        _re = re.compile(
            '<tag wdom_id="\d+">\s*</tag>',
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
        self.assertRegex(elm.html, r'<a wdom_id="\d+"></a>')

    def test_create_element_unknown(self):
        elm = self.doc.createElement('aa')
        self.assertEqual(type(elm), WdomElement)
        self.assertRegex(elm.html, r'<aa wdom_id="\d+"></aa>')

    def test_create_element_defclass(self):
        from wdom import element
        doc = WdomDocument(default_class=element.HTMLElement)
        elm = doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a wdom_id="\d+"></a>')

    def test_create_element_defclass_unknown(self):
        from wdom import element
        doc = WdomDocument(default_class=element.HTMLElement)
        elm = doc.createElement('aa')
        self.assertEqual(type(elm), element.HTMLElement)
        self.assertRegex(elm.html, '<aa></aa>')

    def test_create_custom_element(self):
        class A(WdomElement):
            pass
        self.doc.defaultView.customElements.define('a', A)
        elm = self.doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a wdom_id="\d+"></a>')

    def test_create_custom_element_tag(self):
        class A(Tag):
            tag = 'a'
        self.doc.defaultView.customElements.define('a', A)
        elm = self.doc.createElement('a')
        self.assertEqual(type(elm), A)
        self.assertRegex(elm.html, '<a wdom_id="\d+"></a>')

    def test_custom_tag_theme_tag(self):
        from wdom import themes
        self.doc.register_theme(themes)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, themes.Container))

    def test_custom_tag_theme_default(self):
        from wdom.util import suppress_logging
        suppress_logging()
        from wdom.themes import default
        from wdom import themes
        self.doc.register_theme(default)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, default.Container))
        self.assertTrue(isinstance(elm.firstChild, themes.Container))

    def test_custom_tag_theme(self):
        from wdom.themes import bootstrap3
        from wdom import themes
        self.doc.register_theme(bootstrap3)
        elm = Tag(parent=self.doc.body)
        elm.innerHTML = '<div is="container"></div>'
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.Container))
        self.assertTrue(isinstance(elm.firstChild, themes.Container))
        self.assertIn('maxcdn.bootstrapcdn.com', self.doc.build())

        elm.innerHTML = '<button is="default-button"></button>'
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.DefaultButton))
        self.assertTrue(isinstance(elm.firstChild, bootstrap3.Button))
        self.assertFalse(isinstance(elm.firstChild, themes.DefaultButton))
        self.assertTrue(isinstance(elm.firstChild, themes.Button))

    def test_tempdir(self):
        doc = WdomDocument()
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

    def test_add_eventlistener(self):
        mock = MagicMock(_is_coroutine=False)
        js_mock = MagicMock()
        doc = get_document()
        doc.js_exec = js_mock
        doc.addEventListener('click', mock)
        js_mock.assert_called_once_with('addEventListener', 'click')
        msg = {
            'type': 'click',
            'currentTarget': {'id': 'document'},
            'target': {'id': 'document'},
        }
        e = event_handler(msg)
        mock.assert_called_once_with(e)

    def test_wdom_id(self):
        self.assertEqual(self.doc.wdom_id, 'document')


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
        self.assertIn('WDOM_AUTORELOAD = true', html)
        self.assertNotIn('WDOM_RELOAD_WAIT', html)

    def test_document_reload_wait(self):
        doc = get_new_document(autoreload=True, reload_wait=1234)
        html = doc.build()
        self.assertIn('WDOM_AUTORELOAD = true', html)
        self.assertIn('WDOM_RELOAD_WAIT = 1234', html)

    def test_document_no_reload_wait_no_reload(self):
        doc = get_new_document(autoreload=False, reload_wait=1234)
        html = doc.build()
        self.assertNotIn('WDOM_AUTORELOAD', html)
        self.assertNotIn('WDOM_RELOAD_WAIT', html)

    def test_document_log_level_str(self):
        doc = get_new_document(log_level='INFO')
        html = doc.build()
        self.assertIn('WDOM_LOG_LEVEL = \'INFO\'', html)

    def test_document_log_level_int(self):
        doc = get_new_document(log_level=10)
        html = doc.build()
        self.assertIn('WDOM_LOG_LEVEL = 10', html)

    def test_document_log_prefix(self):
        doc = get_new_document(log_prefix='TEST')
        html = doc.build()
        self.assertIn('WDOM_LOG_PREFIX = \'TEST\'', html)

    def test_document_log_console(self):
        doc = get_new_document(log_console=True)
        html = doc.build()
        self.assertIn('WDOM_LOG_CONSOLE = true', html)

    def test_document_ws_url(self):
        doc = get_new_document(ws_url='test_ws')
        html = doc.build()
        self.assertIn('WDOM_WS_URL = \'test_ws\'', html)
