#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from wdom.node import NamedNodeMap
from wdom.tag import TagBase, PyNode, Tag, DOMTokenList
from wdom.tag import NewTagClass
from wdom.tests.util import TestCase


class TestDom(TestCase):
    '''Test for Basic Dom implementation'''
    def setUp(self):
        self.dom = TagBase()
        self.c1 = TagBase(c="1")
        self.c2 = TagBase(c="2")

    def test_name(self):
        self.assertEqual(self.dom.tag, 'tag')
        self.assertEqual(self.dom.tagName, 'TAG')
        self.assertEqual(self.dom.localName, 'tag')

        class A(TagBase):
            tag = 'Atag'
        a = A()
        self.assertEqual(a.tag, 'Atag')
        self.assertEqual(a.tagName, 'ATAG')
        self.assertEqual(a.localName, 'atag')

    def test_tag_string(self):
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_attr_init(self):
        dom = TagBase(attrs={'src': 'a'})
        self.assertEqual('<tag src="a"></tag>', dom.html)
        dom.removeAttribute('src')
        self.assertEqual('<tag></tag>', dom.html)

    def test_attr_atomic(self):
        # test add tag-attr
        self.dom['a'] = 'b'
        self.assertEqual(self.dom['a'], 'b')
        self.assertIn('a="b"', self.dom.html)
        self.assertEqual('<tag a="b">', self.dom.start_tag)
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
        self.assertEqual(self.dom.attributes['a'].value, 'b')
        self.dom.removeAttribute('a')
        self.assertIsFalse(self.dom.hasAttributes())
        self.assertEqual('<tag></tag>', self.dom.html)
        self.assertEqual(self.dom.attributes, NamedNodeMap())

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
        with self.assertRaises(ValueError):
            self.dom.removeChild(TagBase())
        with self.assertRaises(ValueError):
            self.dom.replaceChild(TagBase(), TagBase())

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
        # self.assertIn('text', self.dom)
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
        self.assertEqual(self.dom.length, 1)
        self.assertEqual('<tag>b</tag>', self.dom.html)
        self.assertIsNone(self.c1.parentNode)

    def test_closing_tag(self):
        class Img(TagBase):
            tag = 'img'
        img = Img()
        self.assertEqual('<img>', img.html)
        img.setAttribute('src', 'a')
        self.assertEqual('<img src="a">', img.html)

    def _test_shallow_copy(self, clone):
        self.assertIsTrue(self.dom.hasChildNodes())
        self.assertIsFalse(clone.hasChildNodes())
        self.assertEqual(len(clone), 0)
        self.assertEqual('<tag src="a" class="b"></tag>', clone.html)

        self.assertIsTrue(clone.hasAttributes())
        self.assertEqual(clone.getAttribute('src'), 'a')
        clone.setAttribute('src', 'b')
        self.assertEqual(clone.getAttribute('src'), 'b')
        self.assertEqual(self.dom.getAttribute('src'), 'a')

        self.assertIsTrue(clone.hasClass('b'))
        self.assertEqual(clone.getAttribute('class'), 'b')
        clone.setAttribute('class', 'c')
        self.assertEqual(clone.getAttribute('class'), 'c')
        self.assertEqual(self.dom.getAttribute('class'), 'b')

        clone.append(self.c2)
        self.assertIsTrue(clone.hasChildNodes())
        self.assertIn(self.c2, clone)
        self.assertNotIn(self.c2, self.dom)

    def test_copy(self):
        from copy import copy
        self.dom.appendChild(self.c1)
        self.dom.setAttribute('src', 'a')
        self.dom.setAttribute('class', 'b')
        clone = copy(self.dom)
        self._test_shallow_copy(clone)

    def test_clone_node_sharrow(self):
        self.dom.appendChild(self.c1)
        self.dom.setAttribute('src', 'a')
        self.dom.setAttribute('class', 'b')
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

        self.c1.setAttribute('class', 'c')
        self.assertEqual(self.c1.getAttribute('class'), 'c')
        self.assertIsNone(clone[0].getAttribute('class'))

        clone.append(self.c2)
        self.assertEqual(len(clone), 2)
        self.assertEqual(len(self.dom), 1)

    def test_deepcopy(self):
        from copy import deepcopy
        self.dom.append(self.c1)
        self.dom.setAttribute('src', 'a')
        self.dom.setAttribute('class', 'b')
        clone = deepcopy(self.dom)
        self._test_deep_copy(clone)

    def test_clone_node_deep(self):
        self.dom.append(self.c1)
        self.dom.setAttribute('src', 'a')
        self.dom.setAttribute('class', 'b')
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
        A = NewTagClass('A', 'a')
        B = NewTagClass('B', 'b')
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
        self.cl = DOMTokenList()

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
        with self.assertRaises(TypeError):
            self.cl.append(1)
        with self.assertRaises(TypeError):
            self.cl.append(TagBase())
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


class TestTagBase(TestCase):
    def setUp(self):
        self.dom = TagBase()
        self.c1 = TagBase()
        self.c2 = TagBase()

    def test_class_addremove(self):
        self.assertIsFalse(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertEqual('<tag></tag>', self.dom.html)
        self.dom.addClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsFalse(self.dom.hasClass('b'))
        self.assertEqual('<tag class="a"></tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsFalse(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_class_in_init(self) -> None:
        dom = TagBase(class_ = 'a')
        self.assertIsTrue(dom.hasClass('a'))
        self.assertIsTrue(dom.hasClasses())
        self.assertEqual('<tag class="a"></tag>', dom.html)
        dom.removeClass('a')
        self.assertIsFalse(dom.hasClass('a'))
        self.assertIsFalse(dom.hasClasses())
        self.assertEqual('<tag></tag>', dom.html)

    def test_class_addremove_multi_string(self):
        self.dom.addClass('a b')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<tag class="a b"></tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<tag class="b"></tag>', self.dom.html)

    def test_class_addremove_multi_list(self):
        self.dom.addClass(['a', 'b'])
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsTrue(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<tag class="a b"></tag>', self.dom.html)
        self.dom.removeClass('a')
        self.assertIsTrue(self.dom.hasClasses())
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))
        self.assertEqual('<tag class="b"></tag>', self.dom.html)

    def test_class_getset(self) -> None:
        self.assertEqual(self.dom['class'], None)
        self.dom.addClass('a')
        self.assertEqual(self.dom['class'], 'a')
        self.dom['class'] = 'b'
        self.assertEqual(self.dom['class'], 'b')
        self.assertIsFalse(self.dom.hasClass('a'))
        self.assertIsTrue(self.dom.hasClass('b'))

    def test_class_remove_error(self) -> None:
        with self.assertLogs('wdom.tag', 'WARNING'):
            self.dom.removeClass('a')

    def test_type_class(self) -> None:
        class A(TagBase):
            tag = 'input'
            type_ = 'button'
        a = A()
        self.assertEqual('<input type="button">', a.html)

    def test_type_init(self) -> None:
        a = TagBase(type='button')
        self.assertEqual('<tag type="button"></tag>', a.html)

    def test_type_attr(self) -> None:
        a = TagBase()
        a.setAttribute('type', 'checkbox')
        self.assertEqual('<tag type="checkbox"></tag>', a.html)

    def test_type_setter(self) -> None:
        class Check(TagBase):
            type_ = 'checkbox'
        a = Check()
        b = Check()
        c = Check()
        b['type'] = 'radio'
        c.setAttribute('type', 'text')
        d = Check()
        self.assertEqual('<tag type="checkbox"></tag>', a.html)
        self.assertEqual('<tag type="radio"></tag>', b.html)
        self.assertEqual('<tag type="text"></tag>', c.html)
        self.assertEqual('<tag type="checkbox"></tag>', d.html)

    def test_hidden(self):
        self.dom.show()
        self.assertEqual('<tag></tag>', self.dom.html)
        self.dom.hide()
        self.assertEqual('<tag hidden></tag>', self.dom.html)
        self.dom.show()
        self.assertEqual('<tag></tag>', self.dom.html)

    def test_clone_node_sharrow_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        clone = self.dom.cloneNode()
        self.assertEqual('<tag class="a"></tag>', clone.html)

        clone.removeClass('a')
        self.assertEqual('<tag></tag>', clone.html)
        self.assertEqual('<tag class="a"><tag></tag></tag>', self.dom.html)

        clone.addClass('b')
        self.assertEqual('<tag class="b"></tag>', clone.html)
        self.assertEqual('<tag class="a"><tag></tag></tag>', self.dom.html)

    def test_clone_node_sharrow_hidden(self):
        self.dom.hide()
        clone = self.dom.cloneNode()
        self.assertEqual('<tag hidden></tag>', clone.html)
        clone.show()
        self.assertEqual('<tag hidden></tag>', self.dom.html)
        self.assertEqual('<tag></tag>', clone.html)

    def test_clone_node_deep_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        self.c1.addClass('b')
        clone = self.dom.cloneNode(deep=True)
        self.assertEqual('<tag class="a"><tag class="b"></tag></tag>', self.dom.html)
        self.assertEqual('<tag class="a"><tag class="b"></tag></tag>', clone.html)

        clone.children[0].removeClass('b')
        self.assertEqual('<tag class="a"><tag class="b"></tag></tag>', self.dom.html)
        self.assertEqual('<tag class="a"><tag></tag></tag>', clone.html)

        self.c1.removeClass('b')
        self.assertEqual('<tag class="a"><tag></tag></tag>', self.dom.html)
        self.assertEqual('<tag class="a"><tag></tag></tag>', clone.html)

        clone.addClass('c')
        self.assertEqual('<tag class="a"><tag></tag></tag>', self.dom.html)
        self.assertEqual('<tag class="a c"><tag></tag></tag>', clone.html)

        clone.removeClass('a')
        self.assertEqual('<tag class="a"><tag></tag></tag>', self.dom.html)
        self.assertEqual('<tag class="c"><tag></tag></tag>', clone.html)

    def test_clone_node_deep_hidden(self):
        self.dom.appendChild(self.c1)
        self.c1.hide()
        clone = self.dom.cloneNode(deep=True)
        self.assertEqual('<tag><tag hidden></tag></tag>', self.dom.html)
        self.assertEqual('<tag><tag hidden></tag></tag>', clone.html)

        self.c1.show()
        self.assertEqual('<tag><tag></tag></tag>', self.dom.html)
        self.assertEqual('<tag><tag hidden></tag></tag>', clone.html)

    def test_class_of_class(self):
        class A(TagBase):
            tag = 'a'
            class_ = 'a1'
        self.assertEqual(A.get_class_list().to_string(), 'a1')
        a = A()
        self.assertEqual('<a class="a1"></a>', a.html)
        a.addClass('a2')
        self.assertEqual('<a class="a1 a2"></a>', a.html)
        with self.assertLogs('wdom.tag', 'WARNING'):
            a.removeClass('a1')
        self.assertEqual('<a class="a1 a2"></a>', a.html)

    def test_classes_multiclass(self):
        class A(TagBase):
            tag = 'a'
            class_ = 'a1 a2'
        self.assertEqual(A.get_class_list().to_string(), 'a1 a2')
        a = A()
        a.addClass('a3 a4')
        self.assertEqual('<a class="a1 a2 a3 a4"></a>', a.html)

    def test_classes_inherit_class(self):
        class A(TagBase):
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
        class A(TagBase):
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
        self.assertMatch(r'<py-node id="\d+"></py-node>', dom.html)

    def test_id_constructor(self):
        dom = PyNode(id='test')
        self.assertEqual('<py-node id="test"></py-node>', dom.html)


class TestTag(TestCase):
    def setUp(self):
        self.dom = Tag()

    def test_event_addremove(self):
        listener = lambda data: None
        listener_2 = lambda data: None
        self.dom.addEventListener('click', listener)
        self.assertMatch(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        )
        # Add listner on same type. one event should be defined in html.
        self.dom.addEventListener('click', listener_2)
        self.assertMatch(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        )

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
        self.assertMatch(r'<node id="\d+"></node>', self.dom.html)


class TestNewClass(TestCase):
    def test_create(self):
        MyTag = NewTagClass('MyTag', 'mt')
        self.assertIsTrue(issubclass(MyTag, Tag))
        self.assertEqual(MyTag.__name__, 'MyTag')
        self.assertEqual(MyTag.tag, 'mt')
        elm = MyTag()
        self.assertEqual(elm.localName, 'mt')
        self.assertMatch(r'<mt id="\d+"></mt>', elm.html)

    def test_create_by_classname(self):
        MyTag = NewTagClass('MyTag')
        self.assertIsTrue(issubclass(MyTag, Tag))
        self.assertEqual(MyTag.__name__, 'MyTag')
        self.assertEqual(MyTag.tag, 'mytag')
        elm = MyTag()
        self.assertMatch(r'<mytag id="\d+"></mytag>', elm.html)

    def test_create_class_with_baseclass(self):
        MyTag = NewTagClass('MyTag', 'mt')
        MyTag2 = NewTagClass('MyTag2', 'mt2', MyTag)
        self.assertIsTrue(issubclass(MyTag2, MyTag))
        self.assertEqual(MyTag2.tag, 'mt2')
        elm = MyTag2()
        self.assertMatch(r'<mt2 id="\d+"></mt2>', elm.html)

        class A(object):
            pass
        MyTag3 = NewTagClass('MyTag3', 'mt3', (MyTag, A))
        self.assertIsTrue(issubclass(MyTag3, MyTag))
        self.assertIsTrue(issubclass(MyTag3, A))

    def test_closing_tag(self):
        Img = NewTagClass('Img')
        img = Img()
        self.assertEqual(img.html, '<img id="{}">'.format(img.id))
        img = Img(src='/image.jpg')
        self.assertIn('id="{}"'.format(img.id), img.html)
        self.assertIn('src="/image.jpg"', img.html)

    def test_create_class_with_class_attr(self):
        MyTag = NewTagClass('MyTag', 'mt', class_='for test')
        elm = MyTag()
        self.assertEqual(elm.html, '<mt class="for test" id="{}"></mt>'.format(elm.id))
        elm2 = MyTag()
        elm2.addClass('new class')
        self.assertEqual(elm2.html, '<mt class="for test new class" id="{}"></mt>'.format(str(id(elm2))))
