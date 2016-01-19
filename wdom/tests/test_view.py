#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom.view import Document
from wdom.dom import Node
from wdom.tests.util import TestCase


class TestMainDocument(TestCase):
    def setUp(self) -> None:
        self.document = Document()

    def test_blankpage(self) -> None:
        _re = re.compile(
            '\s*<!DOCTYPE html>'
            '\s*<head>'
            '\s*<meta charset="utf-8"\s*/?>'
            '\s*<meta content="text/css" http-equiv="Content-Style-Type"\s*/?>'
            '\s*<title>'
            '\s*W-DOM'
            '\s*</title>'
            '\s*<link href="favicon.ico" rel="shortcut icon">'
            '(\s*<style>.*?</style>)?'
            '\s*</head>'
            '\s*<body(\s*unresolved(="")?)?\s*>'
            '(\s*<link href="html/.+\.html" rel="import">)*'
            '\s*<script\s*type="text/javascript">'
            '.*?</script>'
            '\s*</body>'
            '\s*</html>'
            , re.S
        )
        html = self.document.build()
        self.assertIsNotNone(_re.match(html))

    def test_add_jsfile(self) -> None:
        self.document.add_jsfile('jsfile')
        _re = re.compile(
            '<body.*'
            '<script src="jsfile" type="text/javascript">\s*</script>'
            '.*<script',
            re.S
        )
        self.assertIsNotNone(_re.search(self.document.build()))

    def test_add_cssfile(self) -> None:
        self.document.add_cssfile('cssfile')
        _re = re.compile(
            '<head>.*'
            '<link href="cssfile" rel="stylesheet"\s*/?>\s*(</link>)?'
            '.*</head>',
            re.S
        )
        self.assertIsNotNone(_re.search(self.document.build()))

    def test_add_header_link(self) -> None:
        self.document.add_header('<link href="cssfile" rel="stylesheet">')
        _re = re.compile(
            '<head>.*'
            '<link href="cssfile" rel="stylesheet"\s*/?>\s*(</link>)?'
            '.*</head>',
            re.S
        )
        self.assertIsNotNone(_re.search(self.document.build()))

    def test_add_header_script(self) -> None:
        self.document.add_header(
            '<script src="jsfile" type="text/javascript"></script>')
        _re = re.compile(
            '<head>.*'
            '<script src="jsfile" type="text/javascript"></script>'
            '.*</head>',
            re.S
        )
        self.assertIsNotNone(_re.search(self.document.build()))

    def test_title(self) -> None:
        document = Document(title='TEST')
        _re = re.compile(
            '<title>\s*TEST\s*</title>',
            re.S
        )
        html = document.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('W-DOM', html)

    def test_charset(self) -> None:
        document = Document(charset='TEST')
        _re = re.compile(
            '<meta\s+charset="TEST"\s*/?>',
            re.S
        )
        html = document.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('utf', html)

    def test_set_body(self) -> None:
        self.document.set_body(Node())
        html = self.document.build()
        _re = re.compile(
            '<node\s+id="\d+">\s*</node>',
            re.S
        )
        self.assertIsNotNone(_re.search(html))

    def test_set_body_string(self) -> None:
        string = 'testing'
        self.document.set_body(string)
        html = self.document.build()
        self.assertIn(string, html)

    def test_set_body_error(self) -> None:
        with self.assertRaises(TypeError):
            self.document.set_body(1)
