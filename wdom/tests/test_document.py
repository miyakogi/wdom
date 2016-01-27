#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom.document import Document
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
            '\s*<meta charset="utf-8" id="\d+">'
            '\s*<title id="\d+">'
            '\s*W-DOM'
            '\s*</title>'
            '(\s*<style>.*?</style>)?'
            '\s*</head>'
            '\s*<body id="\d+">'
            '\s*<script\s*type="text/javascript" id="\d+">'
            '.*?</script>'
            '\s*</body>'
            '\s*</html>'
            , re.S
        )
        html = self.doc.build()
        self.assertIsNotNone(_re.match(html))

    def test_add_jsfile(self) -> None:
        self.doc.add_jsfile('jsfile')
        _re = re.compile(
            '<body.*'
            '<script( src="jsfile"| type="text/javascript"){2} '
            'id="\d+">\s*</script>'
            '.*</body',
            re.S
        )
        self.assertIsNotNone(_re.search(self.doc.build()))

    def test_add_cssfile(self) -> None:
        self.doc.add_cssfile('cssfile')
        _re = re.compile(
            '<head id="\d+">.*'
            '<link( href="cssfile"| rel="stylesheet"){2} id="\d+">'
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

    def test_charset(self) -> None:
        doc = Document(charset='TEST')
        _re = re.compile(
            '<meta charset="TEST" id="\d+">',
            re.S
        )
        html = doc.build()
        self.assertIsNotNone(_re.search(html))
        self.assertNotIn('utf', html)

    def test_set_body(self) -> None:
        self.doc.set_body(Tag())
        html = self.doc.build()
        _re = re.compile(
            '<node id="\d+">\s*</node>',
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
