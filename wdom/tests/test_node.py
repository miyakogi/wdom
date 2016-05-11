#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest import TestCase
from wdom.node import Node, ParentNode, NonDocumentTypeChildNode, ChildNode
from wdom.node import Text, DocumentType, DocumentFragment
from wdom.node import RawHtml, Comment, CharacterData
from wdom.element import Element


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
        self.assertEqual(self.node.childNodes.index(self.c1), 0)
        self.assertEqual(self.node.childNodes.index(self.c2), 1)
        self.assertEqual(self.node.childNodes.index(self.c3), 2)


class P(Node, ParentNode):
    pass


class NDTC(Node, NonDocumentTypeChildNode):
    pass


class C(Node, ChildNode):
    pass


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

    def test_children(self):
        self.p.appendChild(Text('a'))
        self.p.appendChild(Comment('b'))
        self.assertEqual(self.p.children.length, 0)
        elm1 = Element('c1')
        self.p.appendChild(elm1)
        self.p.appendChild(Text('d'))
        self.assertEqual(self.p.children.length, 1)
        self.assertIs(self.p.firstElementChild, elm1)
        self.assertIs(self.p.lastElementChild, elm1)
        elm2 = Element('c2')
        self.p.appendChild(elm2)
        self.p.appendChild(Text('e'))
        self.assertIs(self.p.firstElementChild, elm1)
        self.assertIs(self.p.lastElementChild, elm2)

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


class TestNonDocumentTypeChildNode(TestCase):
    def setUp(self):
        self.p = P()
        self.c1 = NDTC()
        self.c2 = NDTC()
        self.e1 = Element()
        self.e2 = Element()

    def test_element(self):
        self.p.appendChild(self.c1)
        self.assertIsNone(self.c1.previousElementSibling)
        self.assertIsNone(self.c1.nextElementSibling)
        self.p.appendChild(self.e1)
        self.assertIsNone(self.c1.previousElementSibling)
        self.assertIs(self.c1.nextElementSibling, self.e1)
        self.p.prepend(self.e2)
        self.assertIs(self.c1.previousElementSibling, self.e2)
        self.assertIs(self.c1.nextElementSibling, self.e1)

    def test_element2(self):
        self.p.appendChild(self.e1)
        self.assertIsNone(self.e1.previousElementSibling)
        self.assertIsNone(self.e1.nextElementSibling)


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
        self.df = DocumentFragment()
        self.tnode = Text('text')

    def test_nodename(self):
        self.assertEqual(self.tnode.nodeName, '#text')

    def test_html_escape(self):
        self.assertEqual(self.tnode.html, 'text')
        self.tnode.textContent = '<'
        # not escape it has no parent
        self.assertEqual(self.tnode.html, '<')
        self.df.appendChild(self.tnode)
        # escape its parent is DocumentFragment or Element or...
        self.assertEqual(self.tnode.html, '&lt;')

        self.assertEqual(Text('<', parent=self.df).html, '&lt;')
        self.assertEqual(Text('>', parent=self.df).html, '&gt;')
        self.assertEqual(Text('&', parent=self.df).html, '&amp;')
        self.assertEqual(Text('"', parent=self.df).html, '&quot;')
        self.assertEqual(Text('\'', parent=self.df).html, '&#x27;')

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
        self.elm = P()

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
        self.assertEqual('<!--comment-->', self.elm.firstChild.html)


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
