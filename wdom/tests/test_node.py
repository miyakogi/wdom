#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase
from wdom.css import CSSStyleDeclaration
from wdom.node import DOMTokenList, NamedNodeMap, Attr
from wdom.node import Node, ParentNode, ChildNode
from wdom.node import Text, DocumentType, Document, DocumentFragment
from wdom.node import Element, HTMLElement, RawHtml, Comment, CharacterData


class TestDOMTokenList(TestCase):
    def setUp(self):
        self.tokens = DOMTokenList(self)

    def test_add(self):
        self.assertEqual(self.tokens.length, 0)
        self.assertEqual(self.tokens.toString(), '')

        self.tokens.add('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'a')

        self.tokens.add('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'a')

        self.tokens.add('b')
        self.assertEqual(self.tokens.length, 2)
        self.assertEqual(self.tokens.toString(), 'a b')

        with self.assertRaises(ValueError):
            self.tokens.add('a c')
        with self.assertRaises(ValueError):
            self.tokens.add('a', 'b c')

    def test_remove(self):
        self.tokens.add('a')
        self.tokens.add('b')
        self.assertEqual(self.tokens.length, 2)

        self.tokens.remove('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'b')

        self.tokens.remove('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'b')

        self.tokens.remove('b')
        self.assertEqual(self.tokens.length, 0)
        self.assertEqual(self.tokens.toString(), '')

        with self.assertRaises(ValueError):
            self.tokens.remove('a c')

    def test_toggle(self):
        self.tokens.toggle('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'a')

        self.tokens.toggle('b')
        self.assertEqual(self.tokens.length, 2)
        self.assertEqual(self.tokens.toString(), 'a b')

        self.tokens.toggle('a')
        self.assertEqual(self.tokens.length, 1)
        self.assertEqual(self.tokens.toString(), 'b')

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

    def test_add_multi(self):
        self.tokens.add('a', 'b')
        self.assertEqual(len(self.tokens), 2)
        self.assertEqual('a b', self.tokens.toString())
        self.tokens.remove('a')
        self.assertEqual(len(self.tokens), 1)
        self.assertEqual('b', self.tokens.toString())

    def test_add_multi_string(self):
        # used at initialization of Element
        self.tokens._append('a b')
        self.assertEqual(len(self.tokens), 2)
        self.assertEqual('a b', self.tokens.toString())
        self.tokens.remove('a')
        self.assertEqual(len(self.tokens), 1)
        self.assertEqual('b', self.tokens.toString())

    def test_add_multi_list(self):
        # used at initialization of Element
        self.tokens._append(['a', 'b'])
        self.assertEqual(len(self.tokens), 2)
        self.assertEqual('a b', self.tokens.toString())
        self.tokens.remove('a')
        self.assertEqual(len(self.tokens), 1)
        self.assertEqual('b', self.tokens.toString())

    def test_add_multi_mixed(self):
        # used at initialization of Element
        self.tokens._append(['a', 'b c'])
        self.assertEqual(len(self.tokens), 3)
        self.assertEqual('a b c', self.tokens.toString())
        self.tokens.remove('b')
        self.assertEqual(len(self.tokens), 2)
        self.assertEqual('a c', self.tokens.toString())

    def test_remove_multi(self):
        self.tokens.add('a', 'b', 'c')
        self.tokens.remove('a', 'c')
        self.assertEqual(self.tokens.length, 1)
        self.assertNotIn('a', self.tokens)
        self.assertIn('b', self.tokens)
        self.assertNotIn('c', self.tokens)

    def test_add_none(self):
        with self.assertRaises(TypeError):
            self.tokens.add(None)

    def test_add_blank(self):
        self.tokens.add('')
        self.assertEqual(len(self.tokens), 0)
        self.assertFalse(bool(self.tokens))
        self.assertEqual('', self.tokens.toString())

    def test_add_invlalid(self):
        with self.assertRaises(TypeError):
            self.tokens.add(1)
        with self.assertRaises(TypeError):
            self.tokens.add(Element('a'))
        self.assertEqual(len(self.tokens), 0)
        self.assertFalse(bool(self.tokens))
        self.assertEqual('', self.tokens.toString())

    def test_iter(self):
        cls = ['a', 'b', 'c']
        self.tokens.add(*cls)
        for c in self.tokens:
            self.assertIn(c, cls)
            cls.remove(c)
        self.assertEqual(len(cls), 0)


class TestAttr(TestCase):
    def setUp(self):
        self.id = Attr('id')
        self.cls = Attr('class')
        self.src = Attr('src')

    def test_name(self):
        self.assertEqual(self.id.name, 'id')
        self.assertEqual(self.cls.name, 'class')
        self.assertEqual(self.src.name, 'src')

    def test_value(self):
        self.src.value = 'a'
        self.assertEqual(self.src.value, 'a')

    def test_html(self):
        self.src.value = 'a'
        self.assertEqual(self.src.html, 'src="a"')

    def test_boolean_attr(self):
        hidden = Attr('hidden')
        hidden.value = True
        self.assertEqual(hidden.html, 'hidden')
        hidden.value = False
        self.assertEqual(hidden.html, '')

    def test_isid(self):
        self.assertTrue(self.id.isId)
        self.assertFalse(self.cls.isId)
        self.assertFalse(self.src.isId)


class TestNamedNodeMap(TestCase):
    def setUp(self):
        self.map = NamedNodeMap(self)
        self.attr = Attr('src', value='a')

    def test_addremove(self):
        self.assertEqual(self.map.length, 0)
        self.map.setNamedItem(self.attr)
        self.assertEqual(self.map.length, 1)
        self.assertEqual(self.map.getNamedItem('src').value, 'a')
        self.assertIsNone(self.map.getNamedItem('aaa'))
        self.map.removeNamedItem(Attr('aaa'))
        self.assertEqual(self.map.length, 1)
        self.map.removeNamedItem(Attr('src'))
        self.assertEqual(self.map.length, 0)

    def test_item(self):
        self.map.setNamedItem(self.attr)
        self.assertIsNone(self.map.item(1))
        self.assertIs(self.map.item(0), self.attr)


class TestNode(TestCase):
    def setUp(self):
        self.node = Node()
        self.c1 = Node()
        self.c2 = Node()
        self.c3 = Node()

    def test_attributes(self):
        self.assertFalse(self.node.hasAttributes())

    def test_parent(self):
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

        appended_child1 = self.node.appendChild(self.c1)
        self.assertIs(appended_child1, self.c1)
        self.assertTrue(self.node.hasChildNodes())
        self.assertEqual(len(self.node), 1)
        self.assertEqual(self.node.length, 1)

        appended_child2 = self.node.appendChild(self.c2)
        self.assertIs(appended_child2, self.c2)
        self.assertEqual(len(self.node), 2)
        self.assertEqual(self.node.length, 2)

        removed_child2 = self.node.removeChild(self.c2)
        self.assertIs(removed_child2, self.c2)
        self.assertEqual(len(self.node), 1)
        self.assertEqual(self.node.length, 1)
        self.assertIsNone(self.c2.parentNode)

        removed_child1 = self.node.removeChild(self.c1)
        self.assertIs(removed_child1, self.c1)
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

    def test_insert_before(self):
        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        inserted_node3 = self.node.insertBefore(self.c3, self.c2)

        self.assertIs(inserted_node3, self.c3)
        self.assertIs(self.c3.parentNode, self.node)
        self.assertIs(self.node.childNodes[0], self.c1)
        self.assertIs(self.node.childNodes[1], self.c3)
        self.assertIs(self.node.childNodes[2], self.c2)

    def test_insert_first(self):
        self.node.appendChild(self.c1)
        self.node.appendChild(self.c2)
        inserted_node3 = self.node.insertBefore(self.c3, self.c1)

        self.assertIs(inserted_node3, self.c3)
        self.assertIs(self.c3.parentNode, self.node)
        self.assertIs(self.node.childNodes[0], self.c3)
        self.assertIs(self.node.childNodes[1], self.c1)
        self.assertIs(self.node.childNodes[2], self.c2)

    def test_replace_child(self):
        self.node.appendChild(self.c1)
        self.assertTrue(self.c1 in self.node)
        self.assertFalse(self.c2 in self.node)

        replaced_node = self.node.replaceChild(self.c2, self.c1)
        self.assertIs(replaced_node, self.c1)
        self.assertFalse(self.c1 in self.node)
        self.assertTrue(self.c2 in self.node)
        self.assertIsNone(self.c1.parentNode)
        self.assertIs(self.c2.parentNode, self.node)

    def test_first_last_child(self):
        self.assertIsNone(self.node.firstChild)
        self.assertIsNone(self.node.lastChild)

        self.node.appendChild(self.c1)
        self.assertIs(self.node.firstChild, self.c1)
        self.assertIs(self.node.lastChild, self.c1)

        self.node.appendChild(self.c2)
        self.assertIs(self.node.firstChild, self.c1)
        self.assertIs(self.node.lastChild, self.c2)

    def test_siblings(self):
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

    def test_owner_document(self):
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


class P(Node, ParentNode): pass
class C(Node, ChildNode): pass


def is_equal_nodes(p, nodes2):
    nodes1 = p.childNodes
    assert len(nodes1) == len(nodes2)
    for n1, n2 in zip(nodes1, nodes2):
        if isinstance(n1, Text):
            if isinstance(n2, Text):
                assert n1.textContent == n2.textContent
            elif isinstance(n2, str):
                assert n1.textContent == n2
            else:
                raise AssertionError(n1, n2)
        elif isinstance(n1, Node):
            assert n1 is n2
        else:
            raise AssertionError(n1, n2)


class TestParentNode(TestCase):
    def setUp(self):
        self.p = P()
        self.c1 = C()
        self.c2 = C()
        self.c3 = C()
        self.c4 = C()

    def test_append(self):
        self.assertFalse(self.p.hasChildNodes())
        self.p.append(self.c1)
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 1)
        is_equal_nodes(self.p, [self.c1])

        self.p.append(self.c2)
        self.assertEqual(self.p.length, 2)
        self.assertIs(self.p.firstChild, self.c1)
        self.assertIs(self.p.lastChild, self.c2)
        is_equal_nodes(self.p, [self.c1, self.c2])

    def test_append_multi(self):
        self.p.append(self.c1, self.c2)
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 2)
        is_equal_nodes(self.p, [self.c1, self.c2])

        self.p.append(self.c3, self.c4)
        self.assertEqual(self.p.length, 4)
        is_equal_nodes(self.p, [self.c1, self.c2, self.c3, self.c4])

    def test_append_text(self):
        self.p.append('a')
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 1)
        self.assertTrue(isinstance(self.p.firstChild, Text))
        self.assertEqual(self.p.textContent, 'a')
        is_equal_nodes(self.p, ['a'])

        self.p.append('b')
        self.assertEqual(self.p.length, 2)
        self.assertTrue(isinstance(self.p.firstChild, Text))
        self.assertTrue(isinstance(self.p.lastChild, Text))
        self.assertEqual(self.p.textContent, 'ab')
        is_equal_nodes(self.p, ['a', 'b'])

        self.p.append('c', 'd')
        self.assertEqual(self.p.length, 4)
        self.assertTrue(isinstance(self.p.firstChild, Text))
        self.assertTrue(isinstance(self.p.lastChild, Text))
        self.assertEqual(self.p.textContent, 'abcd')
        is_equal_nodes(self.p, ['a', 'b', 'c', 'd'])

    def test_append_mixed_text_node(self):
        self.p.append(self.c1, 'a', self.c2)
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 3)
        self.assertIs(self.p.firstChild, self.c1)
        self.assertIs(self.p.lastChild, self.c2)
        is_equal_nodes(self.p, [self.c1, 'a', self.c2])

        self.p.append(self.c3, 'b', self.c4)
        is_equal_nodes(self.p, [self.c1, 'a', self.c2, self.c3, 'b', self.c4])

    def test_prepend(self):
        self.p.prepend(self.c1)
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 1)
        is_equal_nodes(self.p, [self.c1])
        self.p.prepend(self.c2)
        is_equal_nodes(self.p, [self.c2, self.c1])

    def test_prepend_multi(self):
        self.p.append(self.c1)
        self.p.prepend(self.c2, self.c3)
        self.assertEqual(self.p.length, 3)
        is_equal_nodes(self.p, [self.c2, self.c3, self.c1])

    def test_prepend_text(self):
        self.p.prepend('a')
        self.assertEqual(self.p.length, 1)
        self.assertTrue(isinstance(self.p.firstChild, Text))
        self.assertEqual(self.p.textContent, 'a')
        is_equal_nodes(self.p, ['a'])

        self.p.prepend('b', 'c')
        self.assertEqual(self.p.length, 3)
        self.assertTrue(isinstance(self.p.firstChild, Text))
        self.assertTrue(isinstance(self.p.lastChild, Text))
        self.assertEqual(self.p.textContent, 'bca')
        is_equal_nodes(self.p, ['b', 'c', 'a'])

    def test_prepend_mixed_text_node(self):
        self.p.prepend(self.c1, 'a', self.c2)
        self.assertTrue(self.p.hasChildNodes())
        self.assertEqual(self.p.length, 3)
        self.assertIs(self.p.firstChild, self.c1)
        self.assertEqual(self.p.textContent, 'a')
        self.assertIs(self.p.lastChild, self.c2)
        is_equal_nodes(self.p, [self.c1, 'a', self.c2])


class TestChildNode(TestCase):
    def setUp(self):
        self.p = P()
        self.c1 = C()
        self.c2 = C()
        self.c3 = C()
        self.c4 = C()
        self.p.append(self.c1, self.c2)

    def test_after(self):
        self.c1.after(self.c3)
        is_equal_nodes(self.p, [self.c1, self.c3, self.c2])

        self.c1.after(self.c4)
        is_equal_nodes(self.p, [self.c1, self.c4, self.c3, self.c2])

    def test_after_text(self):
        self.c1.after('a')
        self.assertIs(self.p.firstChild, self.c1)
        self.assertEqual(self.p.textContent, 'a')
        is_equal_nodes(self.p, [self.c1, 'a', self.c2])

        self.c1.after('b', 'c')
        self.assertEqual(self.p.length, 5)
        self.assertEqual(self.p.textContent, 'bca')
        is_equal_nodes(self.p, [self.c1, 'b', 'c', 'a', self.c2])

    def test_after_multi(self):
        self.c1.after(self.c3, self.c4)
        is_equal_nodes(self.p, [self.c1, self.c3, self.c4, self.c2])

        self.c1.after(self.c2)
        # Is this behaviour correct?
        is_equal_nodes(self.p, [self.c1, self.c2, self.c3, self.c4])

    def test_arter_mixed_text_node(self):
        self.c1.after(self.c3, 'a', self.c4)
        is_equal_nodes(self.p, [self.c1, self.c3, 'a', self.c4, self.c2])

    def test_before(self):
        self.c1.before(self.c3)
        is_equal_nodes(self.p, [self.c3, self.c1, self.c2])

        self.c1.before(self.c4)
        is_equal_nodes(self.p, [self.c3, self.c4, self.c1, self.c2])

    def test_before_text(self):
        self.c1.before('a')
        self.assertEqual(self.p.textContent, 'a')
        is_equal_nodes(self.p, ['a', self.c1, self.c2])

        self.c1.before('b', 'c')
        is_equal_nodes(self.p, ['a', 'b', 'c', self.c1, self.c2])

    def test_before_multi(self):
        self.c2.before(self.c3, self.c4)
        is_equal_nodes(self.p, [self.c1, self.c3, self.c4, self.c2])

    def test_before_mixed(self):
        self.c2.before(self.c3, 'ab', self.c4, 'c')
        self.assertEqual(self.p.textContent, 'abc')
        is_equal_nodes(self.p, [self.c1, self.c3, 'ab', self.c4, 'c', self.c2])

    def test_replace(self):
        self.c1.replaceWith(self.c3)
        is_equal_nodes(self.p, [self.c3, self.c2])

    def test_replace_multi(self):
        self.c1.replaceWith(self.c3, self.c4)
        is_equal_nodes(self.p, [self.c3, self.c4, self.c2])

    def test_replace_text(self):
        self.c1.replaceWith('a', 'b')
        is_equal_nodes(self.p, ['a', 'b', self.c2])

    def test_remove(self):
        self.c2.remove()
        is_equal_nodes(self.p, [self.c1])


class TestCharacterData(TestCase):
    def setUp(self):
        self.node = Node()
        self.tnode = CharacterData('text')

    def test_textcontent(self):
        self.assertEqual(self.tnode.textContent, 'text')
        self.tnode.textContent = 'newtext'
        self.assertEqual(self.tnode.textContent, 'newtext')

    def test_length(self):
        self.assertEqual(self.tnode.length, 4)

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

    def test_invalid_methods(self):
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


class TestText(TestCase):
    def setUp(self):
        self.node = Node()
        self.tnode = Text('text')

    def test_nodename(self):
        self.assertEqual(self.tnode.nodeName, '#text')

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


class TestRawHtml(TestCase):
    def setUp(self):
        pass

    def test_rawhtml_content(self):
        rhtml = RawHtml('<a>')
        self.assertEqual(rhtml.html, '<a>')


class TestComment(TestCase):
    def setUp(self):
        self.c = Comment('comment')
        self.elm = Element('tag')

    def test_node_type(self):
        self.assertEqual(self.c.nodeType, self.c.COMMENT_NODE)
        self.assertEqual(self.c.nodeName, '#comment')

    def test_length(self):
        self.assertEqual(self.c.length, 7)

    def test_html(self):
        self.assertEqual('<!--comment-->', self.c.html)

    def test_append_comment(self):
        self.elm.appendChild(self.c)
        self.assertTrue(self.elm.hasChildNodes())
        self.assertEqual(self.elm.length, 1)
        self.assertEqual('<tag><!--comment--></tag>', self.elm.html)


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
        appended_child = self.df.appendChild(self.elm)
        self.assertEqual(self.df.html, '<a></a>')
        self.assertIs(appended_child, self.elm)

    def test_append_to_element(self):
        appended_child1 = self.df.appendChild(self.c1)
        appended_child2 = self.df.appendChild(self.c2)
        self.assertIs(self.df, self.c1.parentNode)
        self.assertIs(self.df, self.c2.parentNode)
        self.assertIs(appended_child1, self.c1)
        self.assertIs(appended_child2, self.c2)

        appended_df = self.elm.appendChild(self.df)
        self.assertIs(appended_df, self.df)
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

        inserted_node = self.elm.insertBefore(self.df, self.c3)
        self.assertIs(inserted_node, self.df)
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

    def test_child(self):
        appended_child1 = self.df.appendChild(self.c1)
        appended_child2 = self.df.appendChild(self.c2)
        self.assertIs(appended_child1, self.c1)
        self.assertIs(appended_child2, self.c2)
        self.assertEqual(self.c1.html, '<c1></c1>')
        self.assertEqual(self.df.html, '<c1></c1><c2></c2>')

    def test_clone_node_sharrow(self):
        self.df.appendChild(self.c1)
        clone = self.df.cloneNode()
        self.assertEqual(self.df.length, 1)
        self.assertEqual(clone.length, 0)
        clone.appendChild(self.c2)
        self.assertEqual(self.df.length, 1)
        self.assertEqual(clone.length, 1)

    def test_clone_node_deep(self):
        self.df.appendChild(self.c1)
        clone = self.df.cloneNode(deep=True)
        self.assertEqual(self.df.length, 1)
        self.assertEqual(clone.length, 1)
        self.assertEqual(clone.html, '<c1></c1>')

        clone.appendChild(self.c2)
        self.assertEqual(self.df.length, 1)
        self.assertEqual(clone.length, 2)
        self.df.removeChild(self.c1)
        self.assertEqual(self.df.length, 0)
        self.assertEqual(clone.length, 2)


class TestElement(TestCase):
    def setUp(self):
        self.elm = Element('tag')
        self.c1 = Element('c1')
        self.c2 = Element('c2')
        self.c1.classList.add('c1')
        self.c2.classList.add('c2')

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
        with self.assertRaises(TypeError):
            self.elm.appendChild('a')
        self.assertFalse(self.elm.hasChildNodes())

    def test_get_elements_by_tagname(self):
        self.elm.appendChild(self.c1)
        self.elm.appendChild(self.c2)
        c1_tags = self.elm.getElementsByTagName('c1')
        c2_tags = self.elm.getElementsByTagName('c2')
        self.assertEqual(len(c1_tags), 1)
        self.assertEqual(len(c2_tags), 1)
        self.assertIs(c1_tags[0], self.c1)
        self.assertIs(c2_tags[0], self.c2)

    def test_get_elements_by_tagname_nest(self):
        self.elm.appendChild(self.c1)
        self.c1.appendChild(self.c2)
        c2_tags = self.c1.getElementsByTagName('c2')
        self.assertEqual(len(c2_tags), 1)
        self.assertIs(c2_tags[0], self.c2)
        c2_tags = self.elm.getElementsByTagName('c2')
        self.assertEqual(len(c2_tags), 1)
        self.assertIs(c2_tags[0], self.c2)

    def test_get_elements_by_tagname_self(self):
        c1_tags = self.c1.getElementsByTagName('c1')
        self.assertEqual(len(c1_tags), 0)

    def test_get_elements_by_classname(self):
        self.elm.appendChild(self.c1)
        self.elm.appendChild(self.c2)
        c1_classes = self.elm.getElementsByClassName('c1')
        c2_classes = self.elm.getElementsByClassName('c2')
        self.assertEqual(len(c1_classes), 1)
        self.assertEqual(len(c2_classes), 1)
        self.assertIs(c1_classes[0], self.c1)
        self.assertIs(c2_classes[0], self.c2)

    def test_get_elements_by_classname_nest(self):
        self.elm.appendChild(self.c1)
        self.c1.appendChild(self.c2)
        c2_classes = self.c1.getElementsByClassName('c2')
        self.assertEqual(len(c2_classes), 1)
        self.assertIs(c2_classes[0], self.c2)
        c2_classes = self.elm.getElementsByClassName('c2')
        self.assertEqual(len(c2_classes), 1)
        self.assertIs(c2_classes[0], self.c2)

    def test_clone_shallow_child(self):
        self.elm.appendChild(self.c1)
        clone = self.elm.cloneNode()
        self.assertFalse(clone.hasChildNodes())

        clone.appendChild(self.c2)
        self.assertFalse(self.c2 in self.elm)
        self.assertEqual(len(self.elm.childNodes), 1)

    def test_clone_shallow_attr(self):
        self.elm.setAttribute('src', 'a')
        clone = self.elm.cloneNode()

        self.assertTrue(clone.hasAttribute('src'))
        self.assertTrue(clone.getAttribute('src'), 'a')
        self.assertEqual(self.elm.attributes.toString(),
                         clone.attributes.toString())
        clone.setAttribute('src', 'b')
        self.assertNotEqual(self.elm.attributes.toString(),
                            clone.attributes.toString())
        self.assertTrue(self.elm.getAttribute('src'), 'a')
        self.assertTrue(clone.getAttribute('src'), 'b')

    def test_clone_deep_child(self):
        self.elm.appendChild(self.c1)
        clone = self.elm.cloneNode(deep=True)
        self.assertTrue(clone.hasChildNodes())
        self.assertEqual(len(clone.childNodes), 1)
        self.assertTrue(self.c1 in self.elm)
        self.assertFalse(self.c1 in clone)
        self.assertIsNot(self.c1, clone.firstChild)

        clone.appendChild(self.c2)
        self.assertFalse(self.c2 in self.elm)
        self.assertEqual(len(self.elm.childNodes), 1)
        self.assertEqual(len(clone.childNodes), 2)

    def test_clone_deep_attr(self):
        self.elm.setAttribute('src', 'a')
        self.elm.appendChild(self.c1)
        self.c1.setAttribute('src', 'c1')
        clone = self.elm.cloneNode(deep=True)

        self.assertTrue(clone.hasAttribute('src'))
        self.assertTrue(clone.getAttribute('src'), 'a')
        self.assertTrue(clone.firstChild.hasAttribute('src'))
        self.assertTrue(clone.firstChild.getAttribute('src'), 'c1')
        self.assertEqual(self.elm.attributes.toString(),
                         clone.attributes.toString())
        self.assertEqual(self.c1.attributes.toString(),
                         clone.firstChild.attributes.toString())

        clone.firstChild.setAttribute('src', 'b')
        self.assertNotEqual(self.c1.attributes.toString(),
                            clone.firstChild.attributes.toString())
        self.assertTrue(self.c1.getAttribute('src'), 'a')
        self.assertTrue(clone.firstChild.getAttribute('src'), 'b')

    def test_init_class(self):
        elm = Element('a', class_ = 'a')
        self.assertEqual(elm.html, '<a class="a"></a>')
        self.assertEqual(elm.classList.length, 1)
        self.assertIn('a', elm.classList)

        elm2 = Element('a', **{'class': 'b'})
        self.assertEqual(elm2.html, '<a class="b"></a>')
        self.assertEqual(elm2.classList.length, 1)
        self.assertIn('b', elm2.classList)

    def test_init_class_multi_str(self):
        elm = Element('a', class_ = 'a1 a2')
        self.assertEqual(elm.html, '<a class="a1 a2"></a>')
        self.assertEqual(elm.classList.length, 2)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertNotIn('a1 a2', elm.classList)

    def test_init_class_multi_list(self):
        elm = Element('a', class_ = ['a1', 'a2'])
        self.assertEqual(elm.html, '<a class="a1 a2"></a>')
        self.assertEqual(elm.classList.length, 2)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertNotIn('a1 a2', elm.classList)

    def test_init_class_multi_mixed(self):
        elm = Element('a', class_ = ['a1', 'a2 a3'])
        self.assertEqual(elm.html, '<a class="a1 a2 a3"></a>')
        self.assertEqual(elm.classList.length, 3)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertIn('a3', elm.classList)
        self.assertNotIn('a2 a3', elm.classList)


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

    def test_style_invalid_type(self):
        with self.assertRaises(TypeError):
            self.elm.style = 1
        with self.assertRaises(TypeError):
            self.elm.style = self.elm

    def test_init_style_init(self):
        elm = HTMLElement('a', style='color: red;')
        self.assertEqual(elm.style.cssText, 'color: red;')
        self.assertEqual(elm.getAttribute('style'), 'color: red;')
        self.assertEqual(elm.html, '<a style="color: red;"></a>')

    def test_style_setter(self):
        self.elm.style = 'color: red;'
        self.assertEqual(self.elm.style.cssText, 'color: red;')
        self.assertEqual(self.elm.getAttribute('style'), 'color: red;')
        self.assertEqual(self.elm.html, '<a style="color: red;"></a>')

        self.elm.style.color = 'black'
        self.elm.style.background = 'red'
        self.assertEqual(self.elm.style.cssText,
                         'color: black; background: red;')

    def test_style_remove(self):
        self.elm.style = 'color: red;'
        self.elm.removeAttribute('style')
        self.assertIsNotNone(self.elm.style)
        self.assertEqual(self.elm.getAttribute('style'), None)
        self.assertEqual(self.elm.style.cssText, '')

        self.assertEqual(self.elm.html, '<a></a>')

    def test_style_clone(self):
        self.elm.style = 'color: red;'
        clone = self.elm.cloneNode()
        self.assertEqual(clone.style.cssText, 'color: red;')

        clone.style.color = 'black'
        self.assertEqual(clone.style.cssText, 'color: black;')
        self.assertEqual(self.elm.style.cssText, 'color: red;')


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
