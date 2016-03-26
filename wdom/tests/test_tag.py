#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.node import NamedNodeMap
from wdom.tag import Tag, DOMTokenList, NewTagClass
from wdom.tests.util import TestCase


class TestTag(TestCase):
    '''Test for Basic Dom implementation'''
    def setUp(self):
        self.tag = Tag()
        self.c1 = Tag(c="1")
        self.c2 = Tag(c="2")

    def test_name(self):
        self.assertEqual(self.tag.tag, 'tag')
        self.assertEqual(self.tag.tagName, 'TAG')
        self.assertEqual(self.tag.localName, 'tag')

        class A(Tag):
            tag = 'Atag'
        a = A()
        self.assertEqual(a.tag, 'Atag')
        self.assertEqual(a.tagName, 'ATAG')
        self.assertEqual(a.localName, 'atag')

    def test_tag_string(self):
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_attr_init(self):
        tag = Tag(attrs={'src': 'a'})
        self.assertMatch('<tag src="a" id="\d+"></tag>', tag.html)
        tag.removeAttribute('src')
        self.assertMatch('<tag id="\d+"></tag>', tag.html)

    def test_attr_atomic(self):
        # test add tag-attr
        self.tag['a'] = 'b'
        self.assertEqual(self.tag['a'], 'b')
        self.assertIn('a="b"', self.tag.html)
        self.assertMatch('<tag a="b" id="\d+">', self.tag.start_tag)
        self.assertMatch('<tag a="b" id="\d+"></tag>', self.tag.html)
        del self.tag['a']
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_attr_addremove(self):
        self.assertIsFalse(self.tag.hasAttributes())
        self.assertIsFalse(self.tag.hasAttribute('a'))
        self.tag.setAttribute('a', 'b')
        self.assertIsTrue(self.tag.hasAttributes())
        self.assertIsTrue(self.tag.hasAttribute('a'))
        self.assertIsFalse(self.tag.hasAttribute('b'))
        self.assertEqual('b', self.tag.getAttribute('a'))
        self.assertMatch('<tag a="b" id="\d+"></tag>', self.tag.html)
        self.assertEqual(self.tag.attributes['a'].value, 'b')
        self.tag.removeAttribute('a')
        self.assertIsFalse(self.tag.hasAttributes())
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)
        self.assertEqual(self.tag.attributes, NamedNodeMap(self.tag))

        self.assertIsNone(self.tag.getAttribute('aaaa'))

    def test_attr_multi(self):
        self.tag.setAttribute('c', 'd')
        self.tag.setAttribute('e', 'f')
        self.assertIn('c="d"', self.tag.html)
        self.assertIn('e="f"', self.tag.html)

    def test_attr_overwrite(self):
        self.tag.setAttribute('c', 'd')
        self.tag.setAttribute('e', 'f')
        self.tag.setAttribute('c', 'new_d')
        self.assertNotIn('c="d"', self.tag.html)
        self.assertIn('c="new_d"', self.tag.html)
        self.assertIn('e="f"', self.tag.html)

    def test_child_addremove(self):
        self.assertIsFalse(self.tag.hasChildNodes())
        self.tag.appendChild(self.c1)
        self.assertIsTrue(self.tag.hasChildNodes())
        self.assertMatch('<tag id="\d+"><tag c="1" id="\d+"></tag></tag>', self.tag.html)
        self.assertIn(self.c1, self.tag)
        self.tag.removeChild(self.c1)
        self.assertIsFalse(self.tag.hasChildNodes())
        self.assertNotIn(self.c1, self.tag)
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_child_exception(self) -> None:
        with self.assertRaises(ValueError):
            self.tag.removeChild(Tag())
        with self.assertRaises(ValueError):
            self.tag.replaceChild(Tag(), Tag())

    def test_first_last_child(self):
        self.assertIsNone(self.tag.firstChild)
        self.assertIsNone(self.tag.lastChild)
        self.tag.appendChild(self.c1)
        self.assertIs(self.tag.firstChild, self.c1)
        self.assertIs(self.tag.lastChild, self.c1)
        self.tag.appendChild(self.c2)
        self.assertIs(self.tag.firstChild, self.c1)
        self.assertIs(self.tag.lastChild, self.c2)

    def test_child_deep(self):
        self.tag.appendChild(self.c1)
        self.c1.appendChild(self.c2)
        self.assertNotIn(self.c2, self.tag)
        self.assertIn(self.c2, self.c1)
        self.assertMatch('<tag id="\d+"><tag c="1" id="\d+"><tag c="2" id="\d+"></tag></tag></tag>', self.tag.html)

    def test_child_nodes(self):
        self.tag.appendChild(self.c1)
        self.tag.appendChild(self.c2)
        self.assertEqual(len(self.tag.childNodes), 2)
        self.assertIs(self.tag.childNodes[0], self.c1)
        self.assertIs(self.tag.childNodes[1], self.c2)

    def test_child_replace(self):
        self.tag.append(self.c1)
        self.assertIn(self.c1, self.tag)
        self.assertNotIn(self.c2, self.tag)
        self.assertMatch('<tag id="\d+"><tag c="1" id="\d+"></tag></tag>', self.tag.html)

        self.tag.replaceChild(self.c2, self.c1)
        self.assertNotIn(self.c1, self.tag)
        self.assertIn(self.c2, self.tag)
        self.assertMatch('<tag id="\d+"><tag c="2" id="\d+"></tag></tag>', self.tag.html)

    def test_text_addremove(self):
        self.tag.textContent = 'text'
        self.assertIsTrue(self.tag.hasChildNodes())
        self.assertMatch('<tag id="\d+">text</tag>', self.tag.html)
        # self.assertIn('text', self.tag)
        self.assertEqual(self.tag[0].parentNode, self.tag)

        self.tag.textContent = ''
        self.assertIsFalse(self.tag.hasChildNodes())
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_textcontent(self):
        self.assertEqual(self.tag.textContent, '')
        self.tag.textContent = 'a'
        self.assertEqual(self.tag.textContent, 'a')
        self.assertMatch('<tag id="\d+">a</tag>', self.tag.html)
        self.tag.textContent = 'b'
        self.assertEqual(self.tag.textContent, 'b')
        self.assertMatch('<tag id="\d+">b</tag>', self.tag.html)

    def test_textcontent_child(self):
        self.tag.textContent = 'a'
        self.tag.appendChild(self.c1)
        self.assertMatch('<tag id="\d+">a<tag c="1" id="\d+"></tag></tag>', self.tag.html)
        self.c1.textContent = 'c1'
        self.assertMatch('<tag id="\d+">a<tag c="1" id="\d+">c1</tag></tag>', self.tag.html)
        self.assertEqual('ac1', self.tag.textContent)
        self.tag.textContent = 'b'
        self.assertEqual(self.tag.length, 1)
        self.assertMatch('<tag id="\d+">b</tag>', self.tag.html)
        self.assertIsNone(self.c1.parentNode)

    def test_closing_tag(self):
        class Img(Tag):
            tag = 'img'
        img = Img()
        self.assertMatch('<img id="\d+">', img.html)
        img.setAttribute('src', 'a')
        self.assertMatch('<img src="a" id="\d+">', img.html)

    def _test_shallow_copy(self, clone):
        self.assertIsTrue(self.tag.hasChildNodes())
        self.assertIsFalse(clone.hasChildNodes())
        self.assertEqual(len(clone), 0)
        self.assertMatch('<tag src="a" class="b" id="\d+"></tag>', clone.html)

        self.assertIsTrue(clone.hasAttributes())
        self.assertEqual(clone.getAttribute('src'), 'a')
        clone.setAttribute('src', 'b')
        self.assertEqual(clone.getAttribute('src'), 'b')
        self.assertEqual(self.tag.getAttribute('src'), 'a')

        self.assertIsTrue(clone.hasClass('b'))
        self.assertEqual(clone.getAttribute('class'), 'b')
        clone.setAttribute('class', 'c')
        self.assertEqual(clone.getAttribute('class'), 'c')
        self.assertEqual(self.tag.getAttribute('class'), 'b')

        clone.append(self.c2)
        self.assertIsTrue(clone.hasChildNodes())
        self.assertIn(self.c2, clone)
        self.assertNotIn(self.c2, self.tag)

    def test_copy(self):
        from copy import copy
        self.tag.appendChild(self.c1)
        self.tag.setAttribute('src', 'a')
        self.tag.setAttribute('class', 'b')
        clone = copy(self.tag)
        self._test_shallow_copy(clone)

    def test_clone_node_sharrow(self):
        self.tag.appendChild(self.c1)
        self.tag.setAttribute('src', 'a')
        self.tag.setAttribute('class', 'b')
        clone = self.tag.cloneNode()
        self._test_shallow_copy(clone)

        clone2 = self.tag.cloneNode(deep=False)
        self._test_shallow_copy(clone2)

    def _test_deep_copy(self, clone):
        self.assertIsTrue(clone.hasChildNodes())
        self.assertEqual(len(clone), 1)
        self.assertIn(self.c1, self.tag)
        self.assertNotIn(self.c1, clone)

        self.c1.setAttribute('src', 'b')
        self.assertEqual(self.c1.getAttribute('src'), 'b')
        self.assertIsNone(clone[0].getAttribute('src'))

        self.c1.setAttribute('class', 'c')
        self.assertEqual(self.c1.getAttribute('class'), 'c')
        self.assertIsNone(clone[0].getAttribute('class'))

        clone.append(self.c2)
        self.assertEqual(len(clone), 2)
        self.assertEqual(len(self.tag), 1)

    def test_deepcopy(self):
        from copy import deepcopy
        self.tag.append(self.c1)
        self.tag.setAttribute('src', 'a')
        self.tag.setAttribute('class', 'b')
        clone = deepcopy(self.tag)
        self._test_deep_copy(clone)

    def test_clone_node_deep(self):
        self.tag.append(self.c1)
        self.tag.setAttribute('src', 'a')
        self.tag.setAttribute('class', 'b')
        clone = self.tag.cloneNode(deep=True)
        self._test_deep_copy(clone)

    def test_siblings(self):
        self.tag.appendChild(self.c1)
        self.tag.appendChild(self.c2)
        self.assertIsNone(self.tag.previousSibling)
        self.assertIsNone(self.tag.nextSibling)
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
        self.tag.appendChild(a1)
        self.tag.appendChild(a2)
        self.tag.appendChild(b1)
        b1.appendChild(b2)

        a_list = self.tag.getElementsByTagName('a')
        self.assertEqual(len(a_list), 2)
        self.assertIs(a_list[0], a1)
        self.assertIs(a_list[1], a2)

        b_list = self.tag.getElementsByTagName('b')
        self.assertEqual(len(b_list), 2)
        self.assertIs(b_list[0], b1)
        self.assertIs(b_list[1], b2)

        b_sub_list = b1.getElementsByTagName('b')
        self.assertEqual(len(b_sub_list), 1)
        self.assertIs(b_sub_list[0], b2)


class TestClassList(TestCase):
    def setUp(self):
        self.cl = DOMTokenList(self)

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
            self.cl.append(Tag())
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
        self.tag = Tag()
        self.c1 = Tag()
        self.c2 = Tag()

    def test_class_addremove(self):
        self.assertIsFalse(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)
        self.tag.addClass('a')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsTrue(self.tag.hasClass('a'))
        self.assertIsFalse(self.tag.hasClass('b'))
        self.assertMatch('<tag class="a" id="\d+"></tag>', self.tag.html)
        self.tag.removeClass('a')
        self.assertIsFalse(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_class_in_init(self) -> None:
        tag = Tag(class_ = 'a')
        self.assertIsTrue(tag.hasClass('a'))
        self.assertIsTrue(tag.hasClasses())
        self.assertMatch('<tag class="a" id="\d+"></tag>', tag.html)
        tag.removeClass('a')
        self.assertIsFalse(tag.hasClass('a'))
        self.assertIsFalse(tag.hasClasses())
        self.assertMatch('<tag id="\d+"></tag>', tag.html)

    def test_class_addremove_multi_string(self):
        self.tag.addClass('a b')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsTrue(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertMatch('<tag class="a b" id="\d+"></tag>', self.tag.html)
        self.tag.removeClass('a')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertMatch('<tag class="b" id="\d+"></tag>', self.tag.html)

    def test_class_addremove_multi_list(self):
        self.tag.addClass(['a', 'b'])
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsTrue(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertMatch('<tag class="a b" id="\d+"></tag>', self.tag.html)
        self.tag.removeClass('a')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertMatch('<tag class="b" id="\d+"></tag>', self.tag.html)

    def test_class_getset(self) -> None:
        self.assertEqual(self.tag['class'], None)
        self.tag.addClass('a')
        self.assertEqual(self.tag['class'], 'a')
        self.tag['class'] = 'b'
        self.assertEqual(self.tag['class'], 'b')
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))

    def test_class_remove_error(self) -> None:
        with self.assertLogs('wdom.tag', 'WARNING'):
            self.tag.removeClass('a')

    def test_type_class(self) -> None:
        class A(Tag):
            tag = 'input'
            type_ = 'button'
        a = A()
        self.assertMatch('<input type="button" id="\d+">', a.html)

    def test_type_init(self) -> None:
        a = Tag(type='button')
        self.assertMatch('<tag type="button" id="\d+"></tag>', a.html)

    def test_type_attr(self) -> None:
        a = Tag()
        a.setAttribute('type', 'checkbox')
        self.assertMatch('<tag type="checkbox" id="\d+"></tag>', a.html)

    def test_type_setter(self) -> None:
        class Check(Tag):
            type_ = 'checkbox'
        a = Check()
        b = Check()
        c = Check()
        b['type'] = 'radio'
        c.setAttribute('type', 'text')
        d = Check()
        self.assertMatch('<tag type="checkbox" id="\d+"></tag>', a.html)
        self.assertMatch('<tag type="radio" id="\d+"></tag>', b.html)
        self.assertMatch('<tag type="text" id="\d+"></tag>', c.html)
        self.assertMatch('<tag type="checkbox" id="\d+"></tag>', d.html)

    def test_hidden(self):
        self.tag.show()
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)
        self.tag.hide()
        self.assertMatch('<tag hidden id="\d+"></tag>', self.tag.html)
        self.tag.show()
        self.assertMatch('<tag id="\d+"></tag>', self.tag.html)

    def test_clone_node_sharrow_class(self):
        self.tag.appendChild(self.c1)
        self.tag.addClass('a')
        clone = self.tag.cloneNode()
        self.assertMatch('<tag class="a" id="\d+"></tag>', clone.html)

        clone.removeClass('a')
        self.assertMatch('<tag id="\d+"></tag>', clone.html)
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)

        clone.addClass('b')
        self.assertMatch('<tag class="b" id="\d+"></tag>', clone.html)
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)

    def test_clone_node_sharrow_hidden(self):
        self.tag.hide()
        clone = self.tag.cloneNode()
        self.assertMatch('<tag hidden id="\d+"></tag>', clone.html)
        clone.show()
        self.assertMatch('<tag hidden id="\d+"></tag>', self.tag.html)
        self.assertMatch('<tag id="\d+"></tag>', clone.html)

    def test_clone_node_deep_class(self):
        self.tag.appendChild(self.c1)
        self.tag.addClass('a')
        self.c1.addClass('b')
        clone = self.tag.cloneNode(deep=True)
        self.assertMatch('<tag class="a" id="\d+"><tag class="b" id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag class="a" id="\d+"><tag class="b" id="\d+"></tag></tag>', clone.html)

        clone.childNodes[0].removeClass('b')
        self.assertMatch('<tag class="a" id="\d+"><tag class="b" id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', clone.html)

        self.c1.removeClass('b')
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', clone.html)

        clone.addClass('c')
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag class="a c" id="\d+"><tag id="\d+"></tag></tag>', clone.html)

        clone.removeClass('a')
        self.assertMatch('<tag class="a" id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag class="c" id="\d+"><tag id="\d+"></tag></tag>', clone.html)

    def test_clone_node_deep_hidden(self):
        self.tag.appendChild(self.c1)
        self.c1.hide()
        clone = self.tag.cloneNode(deep=True)
        self.assertMatch('<tag id="\d+"><tag hidden id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag id="\d+"><tag hidden id="\d+"></tag></tag>', clone.html)

        self.c1.show()
        self.assertMatch('<tag id="\d+"><tag id="\d+"></tag></tag>', self.tag.html)
        self.assertMatch('<tag id="\d+"><tag hidden id="\d+"></tag></tag>', clone.html)

    def test_class_of_class(self):
        class A(Tag):
            tag = 'a'
            class_ = 'a1'
        self.assertEqual(A.get_class_list().to_string(), 'a1')
        a = A()
        self.assertMatch('<a class="a1" id="\d+"></a>', a.html)
        a.addClass('a2')
        self.assertMatch('<a class="a1 a2" id="\d+"></a>', a.html)
        with self.assertLogs('wdom.tag', 'WARNING'):
            a.removeClass('a1')
        self.assertMatch('<a class="a1 a2" id="\d+"></a>', a.html)

    def test_classes_multiclass(self):
        class A(Tag):
            tag = 'a'
            class_ = 'a1 a2'
        self.assertEqual(A.get_class_list().to_string(), 'a1 a2')
        a = A()
        a.addClass('a3 a4')
        self.assertMatch('<a class="a1 a2 a3 a4" id="\d+"></a>', a.html)

    def test_classes_inherit_class(self):
        class A(Tag):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'

        self.assertEqual(B.get_class_list().to_string(), 'a1 a2 b1 b2')
        b = B()
        b.addClass('b3')
        self.assertMatch('<b class="a1 a2 b1 b2 b3" id="\d+"></b>', b.html)

    def test_classes_notinherit_class(self):
        class A(Tag):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'
            inherit_class = False

        self.assertEqual(B.get_class_list().to_string(), 'b1 b2')
        b = B()
        b.addClass('b3')
        self.assertMatch('<b class="b1 b2 b3" id="\d+"></b>', b.html)

        class C(B):
            tag = 'c'
            class_ = 'c1 c2'
        self.assertEqual(C.get_class_list().to_string(), 'b1 b2 c1 c2')
