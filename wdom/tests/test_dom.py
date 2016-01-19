#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

import pytest
from tornado.testing import ExpectLog

from wdom.dom import TextNode, Dom, HtmlDom, PyNode, Node
from wdom.dom import ClassList, EventListener
from wdom.dom import NewNodeClass
from wdom.tests.util import TestCase


class TestTextNode(TestCase):
    def setUp(self):
        self.text_node = TextNode('text')

    def test_html(self):
        self.assertEqual(TextNode('text').html, 'text')

    def test_html_escape(self):
        self.assertEqual(TextNode('<').html, '&lt;')
        self.assertEqual(TextNode('>').html, '&gt;')
        self.assertEqual(TextNode('&').html, '&amp;')
        self.assertEqual(TextNode('"').html, '&quot;')
        self.assertEqual(TextNode('\'').html, '&#x27;')


class TestDom(TestCase):
    '''Test for Basic Dom implementation'''
    def setUp(self):
        self.dom = Dom()
        self.c1 = Dom(c="1")
        self.c2 = Dom(c="2")

    def test_name(self):
        self.assertEqual(self.dom.tag, 'tag')
        self.assertEqual(self.dom.tagName, 'TAG')
        self.assertEqual(self.dom.localName, 'tag')

        class A(Dom):
            tag = 'Atag'
        a = A()
        self.assertEqual(a.tag, 'Atag')
        self.assertEqual(a.tagName, 'ATAG')
        self.assertEqual(a.localName, 'atag')

    def test_tag_string(self):
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_attr_init(self):
        dom = Dom(attrs={'src': 'a'})
        self.assertEqual('<tag src="a"></tag>', dom.html)
        dom.removeAttribute('src')
        self.assertEqual('<tag></tag>', dom.html)

    def test_attr_atomic(self):
        # test add tag-attr
        self.dom['a'] = 'b'
        self.assertEqual(self.dom['a'], 'b')
        self.assertIn('a="b"', self.dom.html)
        self.assertEqual('<tag a="b">', self.dom.start_tag())
        self.assertEqual('<tag a="b"></tag>', self.dom.html)
        del self.dom['a']
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_attr_addremove(self):
        self.assertIsFalse(self.dom.hasAttributes())
        self.assertIsFalse(self.dom.hasAttribute('a'))
        self.dom.setAttribute('a', 'b')
        self.assertIsTrue(self.dom.hasAttributes())
        self.assertIsTrue(self.dom.hasAttribute('a'))
        self.assertIsFalse(self.dom.hasAttribute('b'))
        self.assertEqual('b', self.dom.getAttribute('a'))
        self.assertEqual('<tag a="b"></tag>', self.dom.html)
        self.assertEqual(self.dom.attributes, {'a': 'b'})
        self.dom.removeAttribute('a')
        self.assertIsFalse(self.dom.hasAttributes())
        self.assertEqual('<tag></tag>', self.dom.html)
        self.assertEqual(self.dom.attributes, {})

        self.assertIsNone(self.dom.getAttribute('aaaa'))

    def test_attr_multi(self):
        self.dom.setAttribute('c', 'd')
        self.dom.setAttribute('e', 'f')
        self.assertIn('c="d"', self.dom.html)
        self.assertIn('e="f"', self.dom.html)

    def test_attr_overwrite(self):
        self.dom.setAttribute('c', 'd')
        self.dom.setAttribute('e', 'f')
        self.dom.setAttribute('c', 'new_d')
        self.assertNotIn('c="d"', self.dom.html)
        self.assertIn('c="new_d"', self.dom.html)
        self.assertIn('e="f"', self.dom.html)

    def test_child_addremove(self):
        self.assertIsFalse(self.dom.hasChildNodes())
        self.dom.appendChild(self.c1)
        self.assertIsTrue(self.dom.hasChildNodes())
        self.assertEqual('<tag><tag c="1"></tag></tag>', self.dom.html)
        self.assertIn(self.c1, self.dom)
        self.dom.removeChild(self.c1)
        self.assertIsFalse(self.dom.hasChildNodes())
        self.assertNotIn(self.c1, self.dom)
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_child_exception(self) -> None:
        with pytest.raises(TypeError):
            self.dom.insert(0, 'a')
        with pytest.raises(TypeError):
            self.dom.append('a')
        with pytest.raises(TypeError):
            self.dom.appendChild('a')

        with pytest.raises(ValueError):
            self.dom.removeChild(Dom())
        with pytest.raises(ValueError):
            self.dom.replaceChild(Dom(), Dom())

    def test_first_last_child(self):
        self.assertIsNone(self.dom.firstChild)
        self.assertIsNone(self.dom.lastChild)
        self.dom.appendChild(self.c1)
        self.assertIs(self.dom.firstChild, self.c1)
        self.assertIs(self.dom.lastChild, self.c1)
        self.dom.appendChild(self.c2)
        self.assertIs(self.dom.firstChild, self.c1)
        self.assertIs(self.dom.lastChild, self.c2)

    def test_child_deep(self):
        self.dom.appendChild(self.c1)
        self.c1.appendChild(self.c2)
        self.assertNotIn(self.c2, self.dom)
        self.assertIn(self.c2, self.c1)
        self.assertEqual('<tag><tag c="1"><tag c="2"></tag></tag></tag>', self.dom.html)

    def test_child_nodes(self):
        self.dom.appendChild(self.c1)
        self.dom.appendChild(self.c2)
        self.assertEqual(len(self.dom.childNodes), 2)
        self.assertIs(self.dom.childNodes[0], self.c1)
        self.assertIs(self.dom.childNodes[1], self.c2)

    def test_child_replace(self):
        self.dom.append(self.c1)
        self.assertIn(self.c1, self.dom)
        self.assertNotIn(self.c2, self.dom)
        self.assertEqual('<tag><tag c="1"></tag></tag>', self.dom.html)
        self.dom.replaceChild(self.c2, self.c1)
        self.assertNotIn(self.c1, self.dom)
        self.assertIn(self.c2, self.dom)
        self.assertEqual('<tag><tag c="2"></tag></tag>', self.dom.html)

    def test_text_addremove(self):
        self.dom.textContent = 'text'
        self.assertIsTrue(self.dom.hasChildNodes())
        self.assertEqual('<tag>text</tag>', self.dom.html)
        self.assertIn('text', self.dom)
        self.assertEqual(self.dom[0].parent, self.dom)

        self.dom.textContent = ''
        self.assertIsFalse(self.dom.hasChildNodes())
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_textcontent(self):
        self.assertEqual(self.dom.textContent, '')
        self.dom.textContent = 'a'
        self.assertEqual(self.dom.textContent, 'a')
        self.assertEqual('<tag>a</tag>', self.dom.html)
        self.dom.textContent = 'b'
        self.assertEqual(self.dom.textContent, 'b')
        self.assertEqual('<tag>b</tag>', self.dom.html)

    def test_textcontent_child(self):
        self.dom.textContent = 'a'
        self.dom.appendChild(self.c1)
        self.assertEqual('<tag>a<tag c="1"></tag></tag>', self.dom.html)
        self.c1.textContent = 'c1'
        self.assertEqual('<tag>a<tag c="1">c1</tag></tag>', self.dom.html)
        self.assertEqual('ac1', self.dom.textContent)
        self.dom.textContent = 'b'
        self.assertEqual('<tag>b</tag>', self.dom.html)
        self.assertIsNone(self.c1.parentNode)

    def test_closing_tag(self):
        class Img(Dom):
            tag = 'img'
        img = Img()
        self.assertEqual('<img>', img.html)
        img.setAttribute('src', 'a')
        self.assertEqual('<img src="a">', img.html)

    def _test_shallow_copy(self, clone):
        self.assertIsTrue(self.dom.hasChildNodes())
        self.assertIsFalse(clone.hasChildNodes())
        self.assertEqual(len(clone), 0)
        self.assertEqual('<tag src="a"></tag>', clone.html)

        self.assertIsTrue(clone.hasAttributes())
        self.assertEqual(clone.getAttribute('src'), 'a')
        clone.setAttribute('src', 'b')
        self.assertEqual(clone.getAttribute('src'), 'b')
        self.assertEqual(self.dom.getAttribute('src'), 'a')

        clone.append(self.c2)
        self.assertIsTrue(clone.hasChildNodes())
        self.assertIn(self.c2, clone)
        self.assertNotIn(self.c2, self.dom)

    def test_copy(self):
        from copy import copy
        self.dom.appendChild(self.c1)
        self.dom.setAttribute('src', 'a')
        clone = copy(self.dom)
        self._test_shallow_copy(clone)

    def test_clone_node_sharrow(self):
        self.dom.appendChild(self.c1)
        self.dom.setAttribute('src', 'a')
        clone = self.dom.cloneNode()
        self._test_shallow_copy(clone)

        clone2 = self.dom.cloneNode(deep=False)
        self._test_shallow_copy(clone2)

    def _test_deep_copy(self, clone):
        self.assertIsTrue(clone.hasChildNodes())
        self.assertEqual(len(clone), 1)
        self.assertIn(self.c1, self.dom)
        self.assertNotIn(self.c1, clone)

        self.c1.setAttribute('src', 'b')
        self.assertEqual(self.c1.getAttribute('src'), 'b')
        self.assertIsNone(clone[0].getAttribute('src'))

        clone.append(self.c2)
        self.assertEqual(len(clone), 2)
        self.assertEqual(len(self.dom), 1)

    def test_deepcopy(self):
        from copy import deepcopy
        self.dom.append(self.c1)
        self.dom.setAttribute('src', 'a')
        clone = deepcopy(self.dom)
        self._test_deep_copy(clone)

    def test_clone_node_deep(self):
        self.dom.append(self.c1)
        self.dom.setAttribute('src', 'a')
        clone = self.dom.cloneNode(deep=True)
        self._test_deep_copy(clone)

    def test_siblings(self):
        self.dom.appendChild(self.c1)
        self.dom.appendChild(self.c2)
        self.assertIsNone(self.dom.previousSibling)
        self.assertIsNone(self.dom.nextSibling)
        self.assertIsNone(self.c1.previousSibling)
        self.assertIs(self.c2.previousSibling, self.c1)
        self.assertIs(self.c1.nextSibling, self.c2)
        self.assertIsNone(self.c2.nextSibling)

    def test_get_elements_by_tagname(self):
        A = NewNodeClass('A', 'a')
        B = NewNodeClass('B', 'b')
        a1 = A(src='a1')
        a2 = A(src='a2')
        b1 = B(src='b1')
        b2 = B(src='b2')
        self.dom.appendChild(a1)
        self.dom.appendChild(a2)
        self.dom.appendChild(b1)
        b1.appendChild(b2)

        a_list = self.dom.getElementsByTagName('a')
        self.assertEqual(len(a_list), 2)
        self.assertIs(a_list[0], a1)
        self.assertIs(a_list[1], a2)

        b_list = self.dom.getElementsByTagName('b')
        self.assertEqual(len(b_list), 2)
        self.assertIs(b_list[0], b1)
        self.assertIs(b_list[1], b2)

        b_sub_list = b1.getElementsByTagName('b')
        self.assertEqual(len(b_sub_list), 1)
        self.assertIs(b_sub_list[0], b2)


class TestClassList(TestCase):
    def setUp(self):
        self.cl = ClassList()

    def test_addremove(self):
        self.assertIsFalse(bool(self.cl))
        self.assertEqual(len(self.cl), 0)
        self.cl.append('a')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 1)
        self.assertIn('a', self.cl)
        self.assertEqual('a', self.cl.to_string())
        self.cl.append('b')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 2)
        self.assertIn('a', self.cl)
        self.assertIn('b', self.cl)
        self.assertEqual('a b', self.cl.to_string())
        self.cl.remove('a')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 1)
        self.assertNotIn('a', self.cl)
        self.assertIn('b', self.cl)
        self.assertEqual('b', self.cl.to_string())

    def test_add_multi_string(self):
        self.cl.append('a b')
        self.assertEqual(len(self.cl), 2)
        self.assertEqual('a b', self.cl.to_string())
        self.cl.remove('a')
        self.assertEqual(len(self.cl), 1)
        self.assertEqual('b', self.cl.to_string())

    def test_add_multi_list(self):
        self.cl.append(['a', 'b'])
        self.assertEqual(len(self.cl), 2)
        self.assertEqual('a b', self.cl.to_string())
        self.cl.remove('a')
        self.assertEqual(len(self.cl), 1)
        self.assertEqual('b', self.cl.to_string())

    def test_add_multi_mixed(self):
        self.cl.append(['a', 'b c'])
        self.assertEqual(len(self.cl), 3)
        self.assertEqual('a b c', self.cl.to_string())
        self.cl.remove('b')
        self.assertEqual(len(self.cl), 2)
        self.assertEqual('a c', self.cl.to_string())

    def test_add_none(self):
        self.cl.append(None)
        self.assertEqual(len(self.cl), 0)
        self.assertIsFalse(bool(self.cl))
        self.assertEqual('', self.cl.to_string())

    def test_add_blank(self):
        self.cl.append('')
        self.assertEqual(len(self.cl), 0)
        self.assertIsFalse(bool(self.cl))
        self.assertEqual('', self.cl.to_string())

    def test_add_invlalid(self):
        with pytest.raises(TypeError):
            self.cl.append(1)
        with pytest.raises(TypeError):
            self.cl.append(Dom())
        self.assertEqual(len(self.cl), 0)
        self.assertIsFalse(bool(self.cl))
        self.assertEqual('', self.cl.to_string())

    def test_iter(self):
        cls = ['a', 'b', 'c']
        self.cl.append(cls)
        for c in self.cl:
            self.assertIn(c, cls)
            cls.remove(c)
        self.assertEqual(len(cls), 0)

    def test_reverse(self):
        self.cl.append('a b c d')
        self.cl.reverse()
        self.assertEqual('d c b a', self.cl.to_string())


class TestHtmlDom(TestCase):
    def setUp(self):
        self.dom = HtmlDom()
        self.c1 = HtmlDom()
        self.c2 = HtmlDom()

    def test_class_addremove(self):
        self.assertIsFalse(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertEqual('<html-tag></html-tag>', self.dom.html)
        self.dom.addClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsFalse(self.dom.hasClass('b'))
        self.assertEqual('<html-tag class="a"></html-tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsFalse(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertEqual('<html-tag></html-tag>', self.dom.html)

    def test_class_in_init(self) -> None:
        dom = HtmlDom(class_ = 'a')
        self.assertIsTrue(dom.hasClass('a'))
        self.assertIsTrue(dom.hasClasses())
        self.assertEqual('<html-tag class="a"></html-tag>', dom.html)
        dom.removeClass('a')
        self.assertIsFalse(dom.hasClass('a'))
        self.assertIsFalse(dom.hasClasses())
        self.assertEqual('<html-tag></html-tag>', dom.html)

    def test_class_addremove_multi_string(self):
        self.dom.addClass('a b')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<html-tag class="a b"></html-tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<html-tag class="b"></html-tag>', self.dom.html)

    def test_class_addremove_multi_list(self):
        self.dom.addClass(['a', 'b'])
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<html-tag class="a b"></html-tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<html-tag class="b"></html-tag>', self.dom.html)

    def test_class_getset(self) -> None:
        self.assertEqual(self.dom['class'], '')
        self.dom.addClass('a')
        self.assertEqual(self.dom['class'], 'a')
        self.dom['class'] = 'b'
        self.assertEqual(self.dom['class'], 'b')
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))

    def test_class_remove_error(self) -> None:
        with ExpectLog('wdom.dom', 'tried to remove non-existing'):
            self.dom.removeClass('a')

    def test_type_class(self) -> None:
        class A(HtmlDom):
            tag = 'input'
            type_ = 'button'
        a = A()
        self.assertEqual('<input type="button">', a.html)

    def test_type_init(self) -> None:
        a = HtmlDom(type='button')
        self.assertEqual('<html-tag type="button"></html-tag>', a.html)

    def test_type_attr(self) -> None:
        a = HtmlDom()
        a.setAttribute('type', 'checkbox')
        self.assertEqual('<html-tag type="checkbox"></html-tag>', a.html)

    def test_type_setter(self) -> None:
        class Check(HtmlDom):
            type_ = 'checkbox'
        a = Check()
        b = Check()
        c = Check()
        b['type'] = 'radio'
        c.setAttribute('type', 'text')
        d = Check()
        self.assertEqual('<html-tag type="checkbox"></html-tag>', a.html)
        self.assertEqual('<html-tag type="radio"></html-tag>', b.html)
        self.assertEqual('<html-tag type="text"></html-tag>', c.html)
        self.assertEqual('<html-tag type="checkbox"></html-tag>', d.html)

    def test_hidden(self):
        self.dom.show()
        self.assertEqual('<html-tag></html-tag>', self.dom.html)
        self.dom.hide()
        self.assertEqual('<html-tag hidden></html-tag>', self.dom.html)
        self.dom.show()
        self.assertEqual('<html-tag></html-tag>', self.dom.html)

    def test_clone_node_sharrow_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        clone = self.dom.cloneNode()
        self.assertEqual('<html-tag class="a"></html-tag>', clone.html)

        clone.removeClass('a')
        self.assertEqual('<html-tag></html-tag>', clone.html)
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', self.dom.html)

        clone.addClass('b')
        self.assertEqual('<html-tag class="b"></html-tag>', clone.html)
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', self.dom.html)

    def test_clone_node_sharrow_hidden(self):
        self.dom.hide()
        clone = self.dom.cloneNode()
        self.assertEqual('<html-tag hidden></html-tag>', clone.html)
        clone.show()
        self.assertEqual('<html-tag hidden></html-tag>', self.dom.html)
        self.assertEqual('<html-tag></html-tag>', clone.html)

    def test_clone_node_deep_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        self.c1.addClass('b')
        clone = self.dom.cloneNode(deep=True)
        self.assertEqual('<html-tag class="a"><html-tag class="b"></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag class="a"><html-tag class="b"></html-tag></html-tag>', clone.html)

        clone.children[0].removeClass('b')
        self.assertEqual('<html-tag class="a"><html-tag class="b"></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', clone.html)

        self.c1.removeClass('b')
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', clone.html)

        clone.addClass('c')
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag class="a c"><html-tag></html-tag></html-tag>', clone.html)

        clone.removeClass('a')
        self.assertEqual('<html-tag class="a"><html-tag></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag class="c"><html-tag></html-tag></html-tag>', clone.html)

    def test_clone_node_deep_hidden(self):
        self.dom.appendChild(self.c1)
        self.c1.hide()
        clone = self.dom.cloneNode(deep=True)
        self.assertEqual('<html-tag><html-tag hidden></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag><html-tag hidden></html-tag></html-tag>', clone.html)

        self.c1.show()
        self.assertEqual('<html-tag><html-tag></html-tag></html-tag>', self.dom.html)
        self.assertEqual('<html-tag><html-tag hidden></html-tag></html-tag>', clone.html)

    def test_class_of_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1'
        self.assertEqual(A.get_class_list().to_string(), 'a1')
        a = A()
        self.assertEqual('<a class="a1"></a>', a.html)
        a.addClass('a2')
        self.assertEqual('<a class="a1 a2"></a>', a.html)
        with ExpectLog('wdom.dom', 'tried to remove class-level class'):
            a.removeClass('a1')
        self.assertEqual('<a class="a1 a2"></a>', a.html)

    def test_classes_multiclass(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'
        self.assertEqual(A.get_class_list().to_string(), 'a1 a2')
        a = A()
        a.addClass('a3 a4')
        self.assertEqual('<a class="a1 a2 a3 a4"></a>', a.html)

    def test_classes_inherit_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'

        self.assertEqual(B.get_class_list().to_string(), 'a1 a2 b1 b2')
        b = B()
        b.addClass('b3')
        self.assertEqual('<b class="a1 a2 b1 b2 b3"></b>', b.html)

    def test_classes_notinherit_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'
            inherit_class = False

        self.assertEqual(B.get_class_list().to_string(), 'b1 b2')
        b = B()
        b.addClass('b3')
        self.assertEqual('<b class="b1 b2 b3"></b>', b.html)

        class C(B):
            tag = 'c'
            class_ = 'c1 c2'
        self.assertEqual(C.get_class_list().to_string(), 'b1 b2 c1 c2')


class TestPyNode(TestCase):
    def test_id_rand(self):
        dom = PyNode()
        self.assertIsNotNone(re.match(r'<py-node id="\d+"></py-node>', dom.html))

    def test_id_constructor(self):
        dom = PyNode(id='test')
        self.assertEqual('<py-node id="test"></py-node>', dom.html)


class TestEventListener(TestCase):
    # To be implemented
    EventListener


class TestNode(TestCase):
    def setUp(self):
        self.dom = Node()

    def test_event_addremove(self):
        listener = lambda data: None
        listener_2 = lambda data: None
        self.dom.addEventListener('click', listener)
        self.assertIsNotNone(re.match(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        ))
        # Add listner on same type. one event should be defined in html.
        self.dom.addEventListener('click', listener_2)
        self.assertIsNotNone(re.match(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        ))

        # Add defferent event type. two event shoud be defined in html.
        self.dom.addEventListener('change', listener)
        self.assertIn('onchange="W.onchange(this);"', self.dom.html)
        self.assertIn('onclick="W.onclick(this);"', self.dom.html)

        # Remove one listener and no listener is define for the event.
        # Only one event shoud be in html.
        self.dom.removeEventListener('change', listener)
        self.assertNotIn('onchange="W.onchange(this);"', self.dom.html)
        self.assertIn('onclick="W.onclick(this);"', self.dom.html)

        # Remove one listener but still have a listener for the event.
        # The event shoud be still define in html.
        self.dom.removeEventListener('click', listener)
        self.assertIn('onclick="W.onclick(this);"', self.dom.html)

        # Remove one more listener and have no listener for the event.
        # No event shoud be still define in html.
        self.dom.removeEventListener('click', listener_2)
        self.assertIsNotNone(re.match(r'<node id="\d+"></node>', self.dom.html))


class TestNewClass(TestCase):
    def test_create(self):
        MyTag = NewNodeClass('MyTag', 'mt')
        self.assertIsTrue(issubclass(MyTag, Node))
        self.assertEqual(MyTag.__name__, 'MyTag')
        self.assertEqual(MyTag.tag, 'mt')
        elm = MyTag()
        self.assertEqual(elm.localName, 'mt')
        self.assertIsNotNone(re.match(r'<mt id="\d+"></mt>', elm.html))

    def test_create_by_classname(self):
        MyTag = NewNodeClass('MyTag')
        self.assertIsTrue(issubclass(MyTag, Node))
        self.assertEqual(MyTag.__name__, 'MyTag')
        self.assertEqual(MyTag.tag, 'mytag')
        elm = MyTag()
        self.assertIsNotNone(re.match(r'<mytag id="\d+"></mytag>', elm.html))

    def test_create_class_with_baseclass(self):
        MyTag = NewNodeClass('MyTag', 'mt')
        MyTag2 = NewNodeClass('MyTag2', 'mt2', MyTag)
        self.assertIsTrue(issubclass(MyTag2, MyTag))
        self.assertEqual(MyTag2.tag, 'mt2')
        elm = MyTag2()
        self.assertIsNotNone(re.match(r'<mt2 id="\d+"></mt2>', elm.html))

        class A(object):
            pass
        MyTag3 = NewNodeClass('MyTag3', 'mt3', (MyTag, A))
        self.assertIsTrue(issubclass(MyTag3, MyTag))
        self.assertIsTrue(issubclass(MyTag3, A))

    def test_closing_tag(self):
        Img = NewNodeClass('Img')
        img = Img()
        self.assertEqual(img.html, '<img id="{}">'.format(img.id))
        img = Img(src='/image.jpg')
        self.assertEqual(img.html, '<img src="/image.jpg" id="{}">'.format(img.id))

    def test_create_class_with_class_attr(self):
        MyTag = NewNodeClass('MyTag', 'mt', class_='for test')
        elm = MyTag()
        self.assertEqual(elm.html, '<mt class="for test" id="{}"></mt>'.format(elm.id))
        elm2 = MyTag()
        elm2.addClass('new class')
        self.assertEqual(elm2.html, '<mt class="for test new class" id="{}"></mt>'.format(str(id(elm2))))
