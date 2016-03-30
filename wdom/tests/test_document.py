#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom import options
from wdom.document import Document, get_document
from wdom.tag import Tag
from wdom.tests.util import TestCase


class TestMainDocument(TestCase):
    def setUp(self) -> None:
        self.doc = Document()

    def test_blankpage(self) -> None:
        _re = re.compile(
            '\s*<!DOCTYPE html>'
            '\s*<html id="\d+">'
            '\s*<head id="\d+">'
            '\s*<meta( charset="utf-8"| id="\d+"){2}>'
            '\s*<title id="\d+">'
            '\s*W-DOM'
            '\s*</title>'
            '(\s*<style>.*?</style>)?'
            '\s*</head>'
            '\s*<body id="\d+">'
            '\s*<script( type="text/javascript"| id="\d+"){2}>'
            '.*?</script>'
            '\s*</body>'
            '\s*</html>'
            , re.S
        )
        html = self.doc.build()
        self.assertIsNotNone(_re.match(html))

    def test_get_element_by_id(self):
        elm = Tag(parent=self.doc.body)
        self.assertIs(elm, self.doc.getElementById(elm.id))
        elm2 = Tag()
        self.assertIsNone(self.doc.getElementById(elm2.id))

    def test_add_jsfile(self) -> None:
        self.doc.add_jsfile('jsfile')
        _re = re.compile(
            '<body.*'
            '<script( src="jsfile"| type="text/javascript"| id="\d+"){3}'
            '>\s*</script>'
            '.*</body',
            re.S
        )
        self.assertIsNotNone(_re.search(self.doc.build()))

    def test_add_cssfile(self) -> None:
        self.doc.add_cssfile('cssfile')
        _re = re.compile(
            '<head id="\d+">.*'
            '<link( href="cssfile"| rel="stylesheet"| id="\d+"){3}>'
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
            '<title id="\d+">\s*TEST\s*</title>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('W-DOM', html)
        self.assertEqual('TEST', doc.title)

    def test_charset(self) -> None:
        doc = Document(charset='TEST')
        _re = re.compile(
            '<meta( charset="TEST"| id="\d+"){2}>',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('utf', html)
        self.assertEqual('TEST', doc.charset)

    def test_set_body(self) -> None:
        self.doc.set_body(Tag())
        html = self.doc.build()
        _re = re.compile(
            '<tag id="\d+">\s*</tag>',
            re.S
        )
        self.assertIsNotNone(_re.search(html))

    def test_set_body_string(self) -> None:
        string = 'testing'
        self.doc.set_body(string)
        html = self.doc.build()
        self.assertIn(string, html)

    def test_set_body_error(self) -> None:
        with self.assertRaises(TypeError):
            self.doc.set_body(1)


class TestDocumentOptions(TestCase):
    def setUp(self):
        options.parse_command_line()

    def test_document_autoreload(self):
        doc = get_document(autoreload=True)
        html = doc.build()
        self.assertIn('RIMO_AUTORELOAD = true', html)
        self.assertNotIn('RIMO_RELOAD_WAIT', html)

    def test_document_reload_wait(self):
        doc = get_document(autoreload=True, reload_wait=1234)
        html = doc.build()
        self.assertIn('RIMO_AUTORELOAD = true', html)
        self.assertIn('RIMO_RELOAD_WAIT = 1234', html)

    def test_document_no_reload_wait_no_reload(self):
        doc = get_document(autoreload=False, reload_wait=1234)
        html = doc.build()
        self.assertNotIn('RIMO_AUTORELOAD', html)
        self.assertNotIn('RIMO_RELOAD_WAIT', html)

    def test_document_log_level_str(self):
        doc = get_document(log_level='INFO')
        html = doc.build()
        self.assertIn('RIMO_LOG_LEVEL = \'INFO\'', html)

    def test_document_log_level_int(self):
        doc = get_document(log_level=10)
        html = doc.build()
        self.assertIn('RIMO_LOG_LEVEL = 10', html)

    def test_document_log_prefix(self):
        doc = get_document(log_prefix='TEST')
        html = doc.build()
        self.assertIn('RIMO_LOG_PREFIX = TEST', html)

    def test_document_log_console(self):
        doc = get_document(log_console=True)
        html = doc.build()
        self.assertIn('RIMO_LOG_CONSOLE = true', html)

    def test_document_ws_url(self):
        doc = get_document(ws_url='test_ws')
        html = doc.build()
        self.assertIn('RIMO_WS_URL = \'test_ws\'', html)
