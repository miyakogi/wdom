#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.element import DOMTokenList
from wdom.tag import Tag, NewTagClass, NestedTag, RawHtmlNode
from wdom.web_node import WdomElement
from wdom.window import customElements

from .base import TestCase


class TestTag(TestCase):
    '''Test for Basic Dom implementation'''
    def setUp(self):
        customElements.clear()
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
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')

    def test_attr_init(self):
        tag = Tag(attrs={'src': 'a'})
        self.assertRegex(tag.html, '<tag wdom_id="\d+" src="a"></tag>')
        tag.removeAttribute('src')
        self.assertRegex(tag.html, '<tag wdom_id="\d+"></tag>')

    def test_attr_addremove(self):
        self.assertFalse(self.tag.hasAttributes())  # wdom_id is not attribute
        self.assertFalse(self.tag.hasAttribute('a'))
        self.tag.setAttribute('a', 'b')
        self.assertTrue(self.tag.hasAttributes())
        self.assertTrue(self.tag.hasAttribute('a'))
        self.assertIsFalse(self.tag.hasAttribute('b'))
        self.assertEqual('b', self.tag.getAttribute('a'))
        self.assertRegex(self.tag.html, r'<tag wdom_id="\d+" a="b"></tag>')
        self.assertEqual(self.tag.getAttribute('a'), 'b')
        self.tag.removeAttribute('a')
        self.assertFalse(self.tag.hasAttributes())  # wdom_id is not attribute
        self.assertFalse(self.tag.hasAttribute('a'))
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')
        self.assertIsNone(self.tag.getAttribute('aaaa'))

    def test_attr_multi(self):
        self.tag.setAttribute('c', 'd')
        self.tag.setAttribute('e', 'f')
        self.assertIn('c="d" e="f"', self.tag.html)

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
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" c="1"></tag></tag>',
        )
        self.assertIn(self.c1, self.tag)
        self.tag.removeChild(self.c1)
        self.assertIsFalse(self.tag.hasChildNodes())
        self.assertNotIn(self.c1, self.tag)
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')

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
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" c="1">'
            '<tag wdom_id="\d+" c="2"></tag></tag></tag>',
        )

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
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" c="1"></tag></tag>',
        )

        self.tag.replaceChild(self.c2, self.c1)
        self.assertNotIn(self.c1, self.tag)
        self.assertIn(self.c2, self.tag)
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" c="2"></tag></tag>',
        )

    def test_text_addremove(self):
        self.tag.textContent = 'text'
        self.assertIsTrue(self.tag.hasChildNodes())
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+">text</tag>')
        # self.assertIn('text', self.tag)
        self.assertEqual(self.tag[0].parentNode, self.tag)

        self.tag.textContent = ''
        self.assertIsFalse(self.tag.hasChildNodes())
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')

    def test_textcontent(self):
        self.assertEqual(self.tag.textContent, '')
        self.tag.textContent = 'a'
        self.assertEqual(self.tag.textContent, 'a')
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+">a</tag>')
        self.tag.textContent = 'b'
        self.assertEqual(self.tag.textContent, 'b')
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+">b</tag>')

    def test_textcontent_child(self):
        self.tag.textContent = 'a'
        self.tag.appendChild(self.c1)
        self.assertRegex(self.tag.html, 'wdom_id="\d+">a<tag .*wdom_id="\d+"')
        self.assertEqual(self.tag.html_noid, '<tag>a<tag c="1"></tag></tag>')
        self.c1.textContent = 'c1'
        self.assertRegex(self.tag.html_noid, '<tag>a<tag c="1">c1</tag></tag>')
        self.assertEqual('ac1', self.tag.textContent)
        self.tag.textContent = 'b'
        self.assertEqual(self.tag.length, 1)
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+">b</tag>')
        self.assertIsNone(self.c1.parentNode)

    def test_closing_tag(self):
        class Img(Tag):
            tag = 'img'
        img = Img()
        self.assertRegex(img.html, '<img wdom_id="\d+">')
        img.setAttribute('src', 'a')
        self.assertRegex(img.html, 'wdom_id="\d+"')
        self.assertEqual(img.html_noid, '<img src="a">')

    def _test_shallow_copy(self, clone):
        self.assertIsTrue(self.tag.hasChildNodes())
        self.assertIsFalse(clone.hasChildNodes())
        self.assertEqual(len(clone), 0)
        self.assertRegex(clone.html, 'wdom_id="\d+"')
        self.assertEqual(clone.html_noid, '<tag src="a" class="b"></tag>')

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

    def test_clone_style(self):
        self.tag.style = 'color: red;'
        clone = self.tag.cloneNode()
        self.assertEqual(clone.html_noid, self.tag.html_noid)

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

    class NewTag(Tag):
        tag = 'new-tag'

    def test_custom_tag(self):
        self.tag.innerHTML = '<new-tag></new-tag>'
        self.assertEqual(type(self.tag.firstChild), WdomElement)
        self.assertFalse(self.tag.firstChild._registered)
        customElements.define('new-tag', self.NewTag)
        self.assertEqual(type(self.tag.firstChild), self.NewTag)
        self.assertTrue(self.tag.firstChild._registered)

    def test_custom_tag_registered(self):
        customElements.define('new-tag', self.NewTag)
        self.c1.innerHTML = '<new-tag></new-tag>'
        self.assertTrue(isinstance(self.c1.firstChild, self.NewTag))
        self.assertTrue(self.c1.firstChild._registered)

    class ExtendTag(Tag):
        tag = 'a'
        is_ = 'new-a'

    def test_custom_tag_is(self):
        self.tag.innerHTML = '<a is="new-a"></a>'
        self.assertEqual(type(self.tag.firstChild), WdomElement)
        self.assertFalse(self.tag.firstChild._registered)
        customElements.define('new-a', self.NewTag, {'extends': 'a'})
        self.assertEqual(type(self.tag.firstChild), self.NewTag)
        self.assertTrue(self.tag.firstChild._registered)

    def test_custom_tag_is_registered(self):
        customElements.define('new-a', self.ExtendTag, {'extends': 'a'})
        self.tag.innerHTML = '<a is="new-a"></a>'
        self.assertEqual(type(self.tag.firstChild), self.ExtendTag)
        self.assertTrue(self.tag.firstChild._registered)

        # test unregistered `is`
        self.tag.innerHTML = '<a is="new-b"></a>'
        self.assertEqual(type(self.tag.firstChild), WdomElement)
        self.assertFalse(self.tag.firstChild._registered)

    def test_custom_tag_define_by_class(self):
        customElements.define(self.NewTag)
        self.tag.innerHTML = '<new-tag></new-tag>'
        self.assertEqual(type(self.tag.firstChild), self.NewTag)

    def test_custom_tag_define_by_class_is(self):
        customElements.define(self.ExtendTag)
        self.tag.innerHTML = '<a is="new-a"></a>'
        self.assertEqual(type(self.tag.firstChild), self.ExtendTag)


class TestNestedTag(TestCase):
    def setUp(self):
        class Inner(Tag):
            tag = 'in'

        class Outer(NestedTag):
            tag = 'out'
            inner_tag_class = Inner
        self.inner_cls = Inner
        self.outer_cls = Outer
        self.tag = self.outer_cls()
        self.c1 = Tag(src='c1')
        self.c2 = Tag(src='c2')
        self.c3 = Tag(src='c3')
        self.c4 = Tag(src='c4')

    def test_tag(self):
        tag = self.outer_cls()
        self.assertRegex(tag.html,
                         r'<out wdom_id="\d+"><in wdom_id="\d+"></in></out>')

    def test_creation(self):
        c = Tag(src='c1')
        tag = self.outer_cls(c, src='out')
        self.assertEqual(
            tag.html_noid,
            '<out src="out"><in><tag src="c1"></tag></in></out>',
        )

    def test_child_node(self):
        self.assertIsNone(self.tag.firstChild)
        self.assertIsNone(self.tag.lastChild)
        self.assertIsNone(self.tag.firstElementChild)
        self.assertIsNone(self.tag.lastElementChild)
        self.tag.appendChild(self.c1)
        self.assertIs(self.tag.firstChild, self.c1)
        self.assertIs(self.tag.lastChild, self.c1)
        self.assertIs(self.tag.firstElementChild, self.c1)
        self.assertIs(self.tag.lastElementChild, self.c1)
        self.assertIsNone(self.c1.previousSibling)
        self.assertIsNone(self.c1.previousElementSibling)
        self.assertIsNone(self.c1.nextSibling)
        self.assertIsNone(self.c1.nextElementSibling)

    def test_addremove_child(self):
        self.tag.append(self.c1, self.c2)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in><tag src="c1"></tag><tag src="c2"></tag></in></out>',
        )
        self.tag.removeChild(self.c1)
        self.assertEqual(
            self.tag.html_noid, '<out><in><tag src="c2"></tag></in></out>')
        self.tag.replaceChild(self.c1, self.c2)
        self.assertEqual(
            self.tag.html_noid, '<out><in><tag src="c1"></tag></in></out>')
        self.c1.replaceWith(self.c2)
        self.assertEqual(
            self.tag.html_noid, '<out><in><tag src="c2"></tag></in></out>')
        self.c2.remove()
        self.assertEqual(
            self.tag.html_noid, '<out><in></in></out>')

    def test_insert(self):
        self.tag.append(self.c1, self.c2)
        self.tag.insertBefore(self.c3, self.c2)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in><tag src="c1"></tag><tag src="c3"></tag>'
            '<tag src="c2"></tag></in></out>',
        )
        self.tag.prepend(self.c4)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in><tag src="c4"></tag><tag src="c1"></tag>'
            '<tag src="c3"></tag><tag src="c2"></tag></in></out>',
        )
        self.tag.empty()
        self.assertEqual(self.tag.html_noid, '<out><in></in></out>')
        self.assertFalse(self.tag.hasChildNodes())
        self.tag.append(self.c1)
        self.c1.before(self.c2)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in><tag src="c2"></tag><tag src="c1"></tag></in></out>',
        )
        self.c1.after(self.c3)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in><tag src="c2"></tag><tag src="c1"></tag>'
            '<tag src="c3"></tag></in></out>',
        )

    def test_inner_content(self):
        self.assertEqual(self.tag.textContent, '')
        self.assertEqual(self.tag.innerHTML, '')
        self.tag.textContent = 'test'
        self.assertEqual(self.tag.textContent, 'test')
        self.assertEqual(self.tag.html_noid, '<out><in>test</in></out>')
        self.tag.append(self.c1)
        self.assertEqual(
            self.tag.html_noid,
            '<out><in>test<tag src="c1"></tag></in></out>',
        )
        self.tag.textContent = 'test2'
        self.assertEqual(self.tag.textContent, 'test2')
        self.assertEqual(self.tag.html_noid, '<out><in>test2</in></out>')
        self.tag.innerHTML = '<a></a>'
        self.assertEqual(self.tag.html_noid, '<out><in><a></a></in></out>')


class TestClassList(TestCase):
    def setUp(self):
        self.cl = DOMTokenList(self)

    def test_addremove(self):
        self.assertIsFalse(bool(self.cl))
        self.assertEqual(len(self.cl), 0)
        self.cl.add('a')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 1)
        self.assertIn('a', self.cl)
        self.assertEqual('a', self.cl.toString())
        self.cl.add('b')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 2)
        self.assertIn('a', self.cl)
        self.assertIn('b', self.cl)
        self.assertEqual('a b', self.cl.toString())
        self.cl.remove('a')
        self.assertIsTrue(bool(self.cl))
        self.assertEqual(len(self.cl), 1)
        self.assertNotIn('a', self.cl)
        self.assertIn('b', self.cl)
        self.assertEqual('b', self.cl.toString())


class TestTagBase(TestCase):
    def setUp(self):
        self.tag = Tag()
        self.c1 = Tag()
        self.c2 = Tag()

    def test_type_class(self) -> None:
        class A(Tag):
            tag = 'input'
            type_ = 'button'
        a = A()
        self.assertRegex(a.html, '<input wdom_id="\d+" type="button">')

    def test_type_init(self) -> None:
        a = Tag(type='button')
        self.assertRegex(a.html, '<tag wdom_id="\d+" type="button"></tag>')

    def test_type_attr(self) -> None:
        a = Tag()
        a.setAttribute('type', 'checkbox')
        self.assertRegex(a.html, '<tag wdom_id="\d+" type="checkbox"></tag>')

    def test_type_setter(self) -> None:
        class Check(Tag):
            type_ = 'checkbox'
        a = Check()
        b = Check()
        c = Check()
        b['type'] = 'radio'
        c.setAttribute('type', 'text')
        d = Check()
        self.assertRegex(a.html, '<tag wdom_id="\d+" type="checkbox"></tag>')
        self.assertRegex(b.html, '<tag wdom_id="\d+" type="radio"></tag>')
        self.assertRegex(c.html, '<tag wdom_id="\d+" type="text"></tag>')
        self.assertRegex(d.html, '<tag wdom_id="\d+" type="checkbox"></tag>')


class TestRawHtmlNode(TestCase):
    def setUp(self):
        self.tag = Tag()
        self.html = '<a>link</a>'

    def test_raw_html(self):
        html_node = RawHtmlNode(self.html)
        self.assertEqual(self.html, html_node.firstChild.html)
        self.assertRegex(
            html_node.html,
            '<div wdom_id="\d+" style="display: inline;">{}</div>'.format(
                self.html)  # no wdom_id in inner tag <a>
        )
