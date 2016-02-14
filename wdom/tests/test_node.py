#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase
from wdom.css import CSSStyleDeclaration
from wdom.node import DOMTokenList, NamedNodeMap
from wdom.node import Node, Attr, Text, DocumentType, Document, DocumentFragment
from wdom.node import Element, HTMLElement, RawHtml, Comment


class TestDOMTokenList(TestCase):
    def setUp(self) -> None:
        self.tokens = DOMTokenList()

    def test_add(self):
        self.assertEqual(self.tokens.length, 0)
        self.assertEqual(self.tokens.to_string(), '')

        self.tokens.add('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'a')

        self.tokens.add('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'a')

        self.tokens.add('b')
        self.assertEqual(self.tokens.length, 2)
        self.assertEqual(self.tokens.to_string(), 'a b')

        with self.assertRaises(ValueError):
            self.tokens.add('a c')

    def test_remove(self):
        self.tokens.add('a')
        self.tokens.add('b')
        self.assertEqual(self.tokens.length, 2)

        self.tokens.remove('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'b')

        self.tokens.remove('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'b')

        self.tokens.remove('b')
        self.assertEqual(self.tokens.length, 0)
        self.assertEqual(self.tokens.to_string(), '')

        with self.assertRaises(ValueError):
            self.tokens.remove('a c')

    def test_toggle(self):
        self.tokens.toggle('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'a')

        self.tokens.toggle('b')
        self.assertEqual(self.tokens.length, 2)
        self.assertEqual(self.tokens.to_string(), 'a b')

        self.tokens.toggle('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.to_string(), 'b')

        with self.assertRaises(ValueError):
            self.tokens.toggle('a c')

    def test_item(self):
        self.assertIsNone(self.tokens.item(1))
        self.tokens.add('a')
        self.assertIsNone(self.tokens.item(1))
        self.tokens.add('b')
        self.assertEqual(self.tokens.item(1), 'b')

    def test_contains(self):
        self.assertFalse(self.tokens.contains('a'))
        self.tokens.add('a')
        self.assertTrue(self.tokens.contains('a'))

        with self.assertRaises(ValueError):
            self.tokens.contains('a c')


class TestNamedNodeMap(TestCase):
    def setUp(self) -> None:
        self.map = NamedNodeMap()
        self.attr = Attr('src', value='a')

    def test_addremove(self):
        self.assertEqual(self.map.length, 0)
        self.map.setNamedItem(self.attr)
        self.assertEqual(self.map.length, 1)
        self.assertEqual(self.map.getNamedItem('src').value, 'a')
        self.assertIsNone(self.map.getNamedItem('aaa'))
        self.map.removeNamedItem('aaa')
        self.assertEqual(self.map.length, 1)
        self.map.removeNamedItem('src')
        self.assertEqual(self.map.length, 0)

    def test_item(self):
        self.map.setNamedItem(self.attr)
        self.assertIsNone(self.map.item(1))
        self.assertIs(self.map.item(0), self.attr)


class TestNode(TestCase):
    def setUp(self) -> None:
        self.node = Node()
        self.c1 = Node()
        self.c2 = Node()
        self.c3 = Node()

    def test_attributes(self) -> None:
        self.assertFalse(self.node.hasAttributes())

    def test_parent(self) -> None:
        self.assertIsNone(self.node.parentNode)
        self.assertIsNone(self.c1.parentNode)
        self.node.appendChild(self.c1)
        self.assertIs(self.node, self.c1.parentNode)

        self.node.removeChild(self.c1)
        self.assertIsNone(self.c1.parentNode)

    def test_parent_init(self):
        node = Node(parent=self.node)
        self.assertTrue(self.node.hasChildNodes())
        self.assertIs(self.node, node.parentNode)
        self.assertFalse(node.hasChildNodes())

    def test_addremove_child(self):
        self.assertFalse(self.node.hasChildNodes())
        self.assertEqual(len(self.node), 0)
        self.assertEqual(self.node.length, 0)

        self.node.appendChild(self.c1)
        self.assertTrue(self.node.hasChildNodes())
        self.assertEqual(len(self.node), 1)
        self.assertEqual(self.node.length, 1)

        self.node.appendChild(self.c2)
        self.assertEqual(len(self.node), 2)
        self.assertEqual(self.node.length, 2)
        self.c2.remove()
        self.assertEqual(len(self.node), 1)
        self.assertEqual(self.node.length, 1)
        self.assertIsNone(self.c2.parentNode)

        self.node.removeChild(self.c1)
        self.assertFalse(self.node.hasChildNodes())
        self.assertEqual(len(self.node), 0)
        self.assertEqual(self.node.length, 0)

        with self.assertRaises(ValueError):
            self.node.removeChild(self.c1)

    def test_empty(self):
        self.node.appendChild(self.c1)
        self.assertTrue(self.node.hasChildNodes())
        self.node.empty()
        self.assertFalse(self.node.hasChildNodes())

        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        self.c1.appendChild(self.c3)
        self.assertTrue(self.node.hasChildNodes())
        self.node.empty()
        self.assertFalse(self.node.hasChildNodes())
        self.assertTrue(self.c1.hasChildNodes())
        self.assertIsNone(self.c1.parentNode)

    def test_insert_before(self) -> None:
        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        self.node.insertBefore(self.c3, self.c2)

        self.assertIs(self.c3.parentNode, self.node)
        self.assertIs(self.node.childNodes[0], self.c1)
        self.assertIs(self.node.childNodes[1], self.c3)
        self.assertIs(self.node.childNodes[2], self.c2)

    def test_insert_first(self) -> None:
        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        self.node.insertBefore(self.c3, self.c1)

        self.assertIs(self.c3.parentNode, self.node)
        self.assertIs(self.node.childNodes[0], self.c3)
        self.assertIs(self.node.childNodes[1], self.c1)
        self.assertIs(self.node.childNodes[2], self.c2)

    def test_replace_child(self) -> None:
        self.node.appendChild(self.c1)
        self.assertTrue(self.c1 in self.node)
        self.assertFalse(self.c2 in self.node)

        self.node.replaceChild(self.c2, self.c1)
        self.assertFalse(self.c1 in self.node)
        self.assertTrue(self.c2 in self.node)
        self.assertIsNone(self.c1.parentNode)
        self.assertIs(self.c2.parentNode, self.node)

    def test_first_last_child(self) -> None:
        self.assertIsNone(self.node.firstChild)
        self.assertIsNone(self.node.lastChild)

        self.node.appendChild(self.c1)
        self.assertIs(self.node.firstChild, self.c1)
        self.assertIs(self.node.lastChild, self.c1)

        self.node.appendChild(self.c2)
        self.assertIs(self.node.firstChild, self.c1)
        self.assertIs(self.node.lastChild, self.c2)

    def test_siblings(self) -> None:
        self.assertIsNone(self.node.previousSibling)
        self.assertIsNone(self.node.nextSibling)

        self.node.appendChild(self.c1)
        self.assertIsNone(self.c1.previousSibling)
        self.assertIsNone(self.c1.nextSibling)

        self.node.appendChild(self.c2)
        self.assertIsNone(self.c1.previousSibling)
        self.assertIs(self.c1.nextSibling, self.c2)
        self.assertIs(self.c2.previousSibling, self.c1)
        self.assertIsNone(self.c2.nextSibling)

    def _test_shallow_copy(self, clone):
        self.assertTrue(self.node.hasChildNodes())
        self.assertFalse(clone.hasChildNodes())
        self.assertEqual(len(clone), 0)

        clone.appendChild(self.c2)
        self.assertTrue(clone.hasChildNodes())
        self.assertIn(self.c2, clone)
        self.assertNotIn(self.c2, self.node)

    def test_copy(self):
        from copy import copy
        self.node.appendChild(self.c1)
        clone = copy(self.node)
        self._test_shallow_copy(clone)

    def test_clone_node_sharrow(self):
        self.node.appendChild(self.c1)
        clone = self.node.cloneNode()
        self._test_shallow_copy(clone)

        clone2 = self.node.cloneNode(deep=False)
        self._test_shallow_copy(clone2)

    def _test_deep_copy(self, clone):
        self.assertTrue(clone.hasChildNodes())
        self.assertEqual(len(clone), 1)
        self.assertIn(self.c1, self.node)
        self.assertNotIn(self.c1, clone)

        clone.appendChild(self.c2)
        self.assertEqual(len(clone), 2)
        self.assertEqual(len(self.node), 1)

    def test_deepcopy(self):
        from copy import deepcopy
        self.node.appendChild(self.c1)
        clone = deepcopy(self.node)
        self._test_deep_copy(clone)

    def test_clone_node_deep(self):
        self.node.appendChild(self.c1)
        clone = self.node.cloneNode(deep=True)
        self._test_deep_copy(clone)

    def test_owner_document(self) -> None:
        self.assertIsNone(self.node.ownerDocument)

    def test_text_content(self):
        self.assertEqual(self.node.textContent, '')
        self.node.textContent = 'a'
        self.assertEqual(self.node.textContent, 'a')
        self.node.textContent = 'b'
        self.assertEqual(self.node.textContent, 'b')

        self.node.appendChild(self.c1)
        self.c1.textContent = 'c1'
        self.assertEqual(self.node.textContent, 'bc1')
        self.node.textContent = 'd'
        self.assertEqual(self.node.textContent, 'd')
        self.assertIsNone(self.c1.parentNode)
        self.assertEqual(self.c1.textContent, 'c1')

    def test_index(self):
        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        self.node.appendChild(self.c3)
        self.assertEqual(self.node.index(self.c1), 0)
        self.assertEqual(self.node.index(self.c2), 1)
        self.assertEqual(self.node.index(self.c3), 2)

class TestAttr(TestCase):
    def setUp(self) -> None:
        self.id = Attr('id')
        self.cls = Attr('class')
        self.src = Attr('src')

    def test_name(self) -> None:
        self.assertEqual(self.id.name, 'id')
        self.assertEqual(self.id.nodeName, 'id')
        self.assertEqual(self.cls.name, 'class')
        self.assertEqual(self.cls.nodeName, 'class')
        self.assertEqual(self.src.name, 'src')
        self.assertEqual(self.src.nodeName, 'src')

    def test_value(self) -> None:
        self.src.value = 'a'
        self.assertEqual(self.src.value, 'a')
        self.assertEqual(self.src.textContent, 'a')
        self.src.textContent = 'b'
        self.assertEqual(self.src.value, 'b')
        self.assertEqual(self.src.textContent, 'b')

    def test_html(self):
        self.src.value = 'a'
        self.assertEqual(self.src.html, 'src="a"')

    def test_boolean_attr(self):
        hidden = Attr('hidden')
        hidden.value = True
        self.assertEqual(hidden.html, 'hidden')
        hidden.value = False
        self.assertEqual(hidden.html, '')

    def test_isid(self) -> None:
        self.assertTrue(self.id.isId)
        self.assertFalse(self.cls.isId)
        self.assertFalse(self.src.isId)

    def test_invalid_methods(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.id.appendChild(self.cls)
        with self.assertRaises(NotImplementedError):
            self.id.removeChild(self.cls)
        with self.assertRaises(NotImplementedError):
            self.id.insertBefore(self.cls, self.src)
        with self.assertRaises(NotImplementedError):
            self.id.replaceChild(self.cls, self.src)
        self.assertFalse(self.id.hasAttributes())
        self.assertFalse(self.id.hasChildNodes())
        self.assertEqual(len(self.id.childNodes), 0)


class TestText(TestCase):
    def setUp(self):
        self.node = Node()
        self.tnode = Text('text')

    def test_nodename(self):
        self.assertEqual(self.tnode.nodeName, '#text')

    def test_textcontent(self):
        self.assertEqual(self.tnode.textContent, 'text')
        self.tnode.textContent = 'newtext'
        self.assertEqual(self.tnode.textContent, 'newtext')

    def test_append_data(self):
        self.tnode.appendData('new')
        self.assertEqual(self.tnode.textContent, 'textnew')

    def test_insert_data(self):
        self.tnode.insertData(1, 'new')
        self.assertEqual(self.tnode.textContent, 'tnewext')

    def test_delete_data(self):
        self.tnode.deleteData(1, 2)
        self.assertEqual(self.tnode.textContent, 'tt')

    def test_replace_data(self):
        self.tnode.replaceData(1, 2, 'new')
        self.assertEqual(self.tnode.textContent, 'tnewt')

    def test_html_escape(self):
        self.assertEqual(self.tnode.html, 'text')
        self.tnode.textContent = '<'
        self.assertEqual(self.tnode.html, '&lt;')

        self.assertEqual(Text('<').html, '&lt;')
        self.assertEqual(Text('>').html, '&gt;')
        self.assertEqual(Text('&').html, '&amp;')
        self.assertEqual(Text('"').html, '&quot;')
        self.assertEqual(Text('\'').html, '&#x27;')

    def test_appned(self):
        self.node.appendChild(self.tnode)
        self.assertTrue(self.node.hasChildNodes())
        self.assertIs(self.tnode.parentNode, self.node)

        node1 = Node()
        node2 = Node()
        self.node.appendChild(node1)
        self.assertIs(self.tnode.nextSibling, node1)
        self.assertIs(self.tnode, node1.previousSibling)

        self.node.insertBefore(node2, self.tnode)
        self.assertIs(self.tnode.previousSibling, node2)
        self.assertIs(self.tnode, node2.nextSibling)

    def test_invalid_methods(self) -> None:
        with self.assertRaises(NotImplementedError):
            self.tnode.appendChild(self.node)
        with self.assertRaises(NotImplementedError):
            self.tnode.removeChild(self.node)
        with self.assertRaises(NotImplementedError):
            self.tnode.insertBefore(self.node, self.node)
        with self.assertRaises(NotImplementedError):
            self.tnode.replaceChild(self.node, self.node)
        self.assertFalse(self.tnode.hasAttributes())
        self.assertFalse(self.tnode.hasChildNodes())
        self.assertEqual(len(self.tnode.childNodes), 0)


class TestRawHtml(TestCase):
    def setUp(self):
        pass

    def test_rawhtml_content(self):
        rhtml = RawHtml('<a>')
        self.assertEqual(rhtml.html, '<a>')

class TestComment(TestCase):
    def setUp(self):
        self.c = Comment('comment')

    def test_html(self):
        self.assertEqual('<!--comment-->', self.c.html)


class TestDocumentType(TestCase):
    def setUp(self):
        self.dtype = DocumentType()
        self.node = Node()

    def test_nodename(self):
        self.assertEqual(self.dtype.nodeName, 'html')
        self.assertEqual(self.dtype.name, 'html')

    def test_parent(self):
        self.node.appendChild(self.dtype)
        self.assertIs(self.node, self.dtype.parentNode)

    def test_html(self):
        self.assertEqual(self.dtype.html, '<!DOCTYPE html>')


class TestDocumentFragment(TestCase):
    def setUp(self):
        self.df = DocumentFragment()
        self.elm = Element('a')
        self.c1 = Element('c1')
        self.c2 = Element('c2')
        self.c3 = Element('c3')

    def test_nodename(self):
        self.assertEqual(self.df.nodeName, '#document-fragment')

    def test_children(self):
        self.assertFalse(self.df.hasChildNodes())
        self.df.appendChild(self.elm)
        self.assertEqual(self.df.html, '<a></a>')

    def test_init_append(self):
        df = DocumentFragment(self.c1, self.c2)
        self.assertEqual(df.length, 2)
        self.assertIs(df.childNodes[0], self.c1)
        self.assertIs(df.childNodes[1], self.c2)
        self.assertIs(df.firstChild, self.c1)
        self.assertIs(df.lastChild, self.c2)

    def test_append_to_element(self):
        self.df.appendChild(self.c1)
        self.df.appendChild(self.c2)
        self.assertIs(self.df, self.c1.parentNode)
        self.assertIs(self.df, self.c2.parentNode)

        self.elm.appendChild(self.df)
        self.assertEqual(self.df.length, 0)
        self.assertEqual(self.elm.length, 2)
        self.assertFalse(self.df.hasChildNodes())
        self.assertIsNone(self.df.parentNode)
        self.assertIs(self.elm, self.c1.parentNode)
        self.assertIs(self.elm, self.c2.parentNode)
        self.assertIsNone(self.df.parentNode)

    def test_insert_to_element(self):
        self.df.appendChild(self.c1)
        self.df.appendChild(self.c2)
        self.elm.appendChild(self.c3)

        self.elm.insertBefore(self.df, self.c3)
        self.assertEqual(self.df.length, 0)
        self.assertEqual(self.elm.length, 3)
        self.assertFalse(self.df.hasChildNodes())
        self.assertIsNone(self.df.parentNode)
        self.assertIs(self.elm, self.c1.parentNode)
        self.assertIs(self.elm, self.c2.parentNode)

        self.assertIsNone(self.c1.previousSibling)
        self.assertIs(self.c1.nextSibling, self.c2)
        self.assertIs(self.c2.previousSibling, self.c1)
        self.assertIs(self.c2.nextSibling, self.c3)
        self.assertIs(self.c3.previousSibling, self.c2)
        self.assertIsNone(self.c3.nextSibling)
        self.assertIs(self.elm.firstChild, self.c1)
        self.assertIs(self.elm.lastChild, self.c3)


class TestElement(TestCase):
    def setUp(self):
        self.elm = Element('tag')
        self.c1 = Element()
        self.c2 = Element()

    def test_constructor(self):
        elm = Element('a')
        self.assertEqual(elm.nodeName, 'A')
        self.assertEqual(elm.tagName, 'A')
        self.assertEqual(elm.localName, 'a')

        self.assertFalse(elm.hasChildNodes())
        self.assertFalse(elm.hasAttributes())

    def test_init_attrs(self):
        elm = Element('a', src='b', href='c')
        self.assertFalse(elm.hasChildNodes())
        self.assertTrue(elm.hasAttributes())
        self.assertTrue(elm.getAttribute('src'), 'b')
        self.assertTrue(elm.getAttribute('href'), 'c')

    def test_attrs(self):
        self.assertIsNone(self.elm.getAttribute('a'))
        self.elm.setAttribute('src', 'a')
        self.assertEqual(self.elm.getAttribute('src'), 'a')
        self.assertTrue(self.elm.hasAttributes())

        self.elm.removeAttribute('src')
        self.assertIsNone(self.elm.getAttribute('src'))
        self.assertFalse(self.elm.hasAttributes())

    def test_id(self):
        self.assertEqual(self.elm.id, '')
        self.elm.setAttribute('id', 'a')
        self.assertEqual(self.elm.getAttribute('id'), 'a')
        self.assertEqual(self.elm.id, 'a')
        self.elm.id = 'b'
        self.assertEqual(self.elm.getAttribute('id'), 'b')
        self.assertEqual(self.elm.id, 'b')

    def test_class_list(self):
        self.assertIsNone(self.elm.getAttribute('class'))
        self.assertFalse(self.elm.hasAttribute('class'))
        self.assertFalse(self.elm.hasAttributes())

        self.elm.setAttribute('class', 'a')
        self.assertEqual(self.elm.getAttribute('class'), 'a')
        self.assertTrue(self.elm.hasAttribute('class'))
        self.assertTrue(self.elm.hasAttributes())

        self.elm.removeAttribute('class')
        self.assertIsNone(self.elm.getAttribute('class'))
        self.assertFalse(self.elm.hasAttribute('class'))
        self.assertFalse(self.elm.hasAttributes())

    def test_start_tag(self):
        self.assertEqual(self.elm.start_tag, '<tag>')
        self.elm.setAttribute('src', 'a')
        self.assertEqual(self.elm.start_tag, '<tag src="a">')

        self.elm.setAttribute('class', 'b')
        self.assertEqual(self.elm.start_tag, '<tag src="a" class="b">')

        self.elm.id = 'c'
        self.assertIn('src="a"', self.elm.start_tag)
        self.assertIn('id="c"', self.elm.start_tag)

    def test_inner_html(self):
        self.assertEqual(self.elm.innerHTML, '')
        self.elm.appendChild(Element('a'))
        self.assertEqual(self.elm.innerHTML, '<a></a>')

        self.elm.innerHTML = '<b></b>'
        self.assertEqual(self.elm.innerHTML, '<b></b>')

    def test_end_tag(self):
        self.assertEqual(self.elm.end_tag, '</tag>')

    def test_html(self):
        self.assertEqual(self.elm.html, '<tag></tag>')

    def test_append_string(self):
        self.elm.appendChild('a')
        self.assertTrue(self.elm.hasChildNodes())


class TestHTMLElement(TestCase):
    def setUp(self):
        self.elm = HTMLElement('a')

    def test_empty_tag(self):
        img = HTMLElement('img')
        self.assertEqual(img.end_tag, '')

    def test_draggable(self):
        n = HTMLElement('img')
        n.draggable = True
        self.assertEqual(n.start_tag, '<img draggable>')

    def test_hidden(self):
        n = HTMLElement('img')
        n.hidden = True
        self.assertEqual(n.start_tag, '<img hidden>')

    def test_title(self):
        n = HTMLElement('img')
        n.title = 'Image'
        self.assertEqual(n.start_tag, '<img title="Image">')

    def test_init_attrs(self):
        elm = HTMLElement('a', src='b', hidden=True)
        self.assertFalse(elm.hasChildNodes())
        self.assertTrue(elm.hasAttributes())
        self.assertTrue(elm.getAttribute('src'), 'b')
        self.assertTrue(elm.hidden)

    def test_style_empty(self):
        self.assertIsNotNone(self.elm.style)
        self.assertEqual(self.elm.getAttribute('style'), None)
        self.assertEqual(self.elm.style.cssText, '')
        self.assertTrue(isinstance(self.elm.style, CSSStyleDeclaration))

        self.assertEqual(self.elm.html, '<a></a>')

    def test_init_style_string(self):
        elm = HTMLElement('a', style='color: red;')
        self.assertEqual(elm.style.cssText, 'color: red;')
        self.assertEqual(elm.getAttribute('style'), 'color: red;')

        self.assertEqual(elm.html, '<a style="color: red;"></a>')

    def test_style_setter(self):
        self.elm.style='color: red;'
        self.assertEqual(self.elm.style.cssText, 'color: red;')
        self.assertEqual(self.elm.getAttribute('style'), 'color: red;')

        self.assertEqual(self.elm.html, '<a style="color: red;"></a>')

    def test_style_remove(self):
        self.elm.style='color: red;'
        self.elm.removeAttribute('style')
        self.assertIsNotNone(self.elm.style)
        self.assertEqual(self.elm.getAttribute('style'), None)
        self.assertEqual(self.elm.style.cssText, '')

        self.assertEqual(self.elm.html, '<a></a>')


class TestDocument(TestCase):
    def setUp(self):
        self.doc = Document()

    def test_nodename(self):
        self.assertEqual(self.doc.nodeName, '#document')

    def test_header(self):
        doc = Document(title='TEST', charset='utf8')
        self.assertTrue(doc.hasChildNodes())
        self.assertEqual(doc.title, 'TEST')
        self.assertEqual(doc.charset, 'utf8')
        self.assertFalse(doc.body.hasChildNodes())

        self.assertTrue(doc.render().startswith('<!DOCTYPE html><html><head>'))
        self.assertTrue(doc.render().endswith('</head><body></body></html>'))
