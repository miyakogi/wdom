#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.tests.util import TestCase

from wdom.node import Node
from wdom.parser import DocumentParser, FragmentParser


class TestDocumentParser(TestCase):
    def setUp(self):
        self.parser = DocumentParser()


class TestFragmentParser(TestCase):
    def setUp(self):
        self.parser = FragmentParser()

    def test_empty(self):
        self.parser.feed('')
        self.assertEqual(self.parser.root.length, 0)
        self.assertEqual(self.parser.root.nodeType,
                         Node.DOCUMENT_FRAGMENT_NODE)

    def test_single_tag(self):
        self.parser.feed('<h1>test</h1>')
        self.assertEqual(self.parser.root.length, 1)
        child = self.parser.root.firstChild
        self.assertEqual(child.nodeType, Node.ELEMENT_NODE)
        self.assertEqual(child.textContent, 'test')
        self.assertEqual(child.textContent, 'test')

    def test_string(self):
        self.parser.feed('a')
        self.assertEqual(self.parser.root.length, 1)
        child = self.parser.root.firstChild
        self.assertEqual(child.nodeType, Node.TEXT_NODE)
        self.assertEqual(child.textContent, 'a')

    def test_multi_tag_para(self):
        self.parser.feed('<h1>test1</h1><h2>test2</h2><h3>test3</h3>')
        self.assertEqual(self.parser.root.length, 3)
        child1 = self.parser.root.childNodes[0]
        child2 = self.parser.root.childNodes[1]
        child3 = self.parser.root.childNodes[2]
        self.assertEqual(child1.length, 1)
        self.assertEqual(child2.length, 1)
        self.assertEqual(child3.length, 1)
        self.assertEqual(child1.tagName, 'H1')
        self.assertEqual(child2.tagName, 'H2')
        self.assertEqual(child3.tagName, 'H3')
        self.assertEqual(child1.textContent, 'test1')
        self.assertEqual(child2.textContent, 'test2')
        self.assertEqual(child3.textContent, 'test3')

    def test_multi_tag_nest(self):
        self.parser.feed('<h1>test1<h2>test2<h3>test3</h3></h2></h1>')
        self.assertEqual(self.parser.root.length, 1)
        child1 = self.parser.root.childNodes[0]
        self.assertEqual(child1.length, 2)  # text and h2
        child2 = child1.lastChild
        self.assertEqual(child2.length, 2)  # text and h3
        child3 = child2.lastChild
        self.assertEqual(child3.length, 1)  # only text

        self.assertEqual(child1.textContent, 'test1test2test3')
        self.assertEqual(child2.textContent, 'test2test3')
        self.assertEqual(child3.textContent, 'test3')

    def test_multi_tag_para_nest(self):
        self.parser.feed(
            '<h1>test1<h2>test2</h2></h1><h3>test3<h4>test4</h4></h3>')
        self.assertEqual(self.parser.root.length, 2)

        child1 = self.parser.root.childNodes[0]
        child2 = child1.childNodes[1]
        child3 = self.parser.root.childNodes[1]
        child4 = child3.childNodes[1]

        self.assertEqual(child1.length, 2)  # text and h2
        self.assertEqual(child2.length, 1)  # only text
        self.assertEqual(child3.length, 2)  # text and h4
        self.assertEqual(child4.length, 1)  # only text

        self.assertEqual(child1.tagName, 'H1')
        self.assertEqual(child2.tagName, 'H2')
        self.assertEqual(child3.tagName, 'H3')
        self.assertEqual(child4.tagName, 'H4')

    def test_empty_tag(self):
        self.parser.feed('<h1><img src="a"></h1>')
        self.assertEqual(self.parser.root.length, 1)
        h1 = self.parser.root.firstChild
        self.assertEqual(h1.length, 1)
        img = h1.firstChild
        self.assertEqual(img.length, 0)
        self.assertEqual(img.tagName, 'IMG')

    def test_empty_tag_only(self):
        self.parser.feed('<img src="a">')
        self.assertEqual(self.parser.root.length, 1)
        img = self.parser.root.firstChild
        self.assertEqual(img.length, 0)
        self.assertEqual(img.tagName, 'IMG')

    def test_empty_tag_para(self):
        self.parser.feed('<h1><img src="a"><img src="b"></h1>')
        self.assertEqual(self.parser.root.length, 1)
        h1 = self.parser.root.firstChild
        self.assertEqual(h1.length, 2)
        img1 = h1.firstChild
        self.assertEqual(img1.length, 0)
        self.assertEqual(img1.tagName, 'IMG')
        self.assertEqual(img1.getAttribute('src'), 'a')
        img2 = h1.lastChild
        self.assertEqual(img2.length, 0)
        self.assertEqual(img2.tagName, 'IMG')
        self.assertEqual(img2.getAttribute('src'), 'b')

    def test_empty_tag_text(self):
        self.parser.feed('<h1>test1<img src="a">test2</h1>')
        self.assertEqual(self.parser.root.length, 1)
        h1 = self.parser.root.firstChild
        self.assertEqual(h1.length, 3)
        self.assertEqual(h1.textContent, 'test1test2')

        img = h1.childNodes[1]
        self.assertEqual(img.length, 0)
