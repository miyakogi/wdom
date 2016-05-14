#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import gc
from unittest import skipIf

from wdom.css import CSSStyleDeclaration
from wdom.node import Text
from wdom.element import (
    DOMTokenList, NamedNodeMap, Attr, Element, HTMLElement,
    HTMLSelectElement, HTMLOptionElement,
)
from wdom.window import customElements
from wdom.testing import TestCase


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

    def test_escape(self):
        self.src.value = '"a"'
        self.assertEqual(self.src.html, 'src="&quot;a&quot;"')

    @skipIf(True, 'Now Attr node need owner element to check boolean')
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


class TestElementMeta(TestCase):
    def setUp(self):
        class NewTag(Element):
            _special_attr_string = ['a', 'b']
            _special_attr_boolean = ['c', 'd']
        self.tag = NewTag('a')

    def check_noattr(self, attr):
        self.assertNotIn(attr, self.tag.attributes)
        self.assertFalse(self.tag.hasAttribute(attr))
        self.assertIsNone(self.tag.getAttribute(attr))

    def check_hasattr(self, attr):
        self.assertIn(attr, self.tag.attributes)
        self.assertTrue(self.tag.hasAttribute(attr))

    def test_special_attr_str(self):
        for attr in ['a', 'b', 'c', 'd', 'e']:
            self.check_noattr(attr)
        self.assertEqual(self.tag.a, '')
        self.assertEqual(self.tag.b, '')
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_str_setter(self):
        self.tag.a = 'a'
        self.check_hasattr('a')
        self.assertEqual(self.tag.a, 'a')
        self.assertEqual(self.tag.getAttribute('a'), 'a')
        self.assertEqual(self.tag.html, '<a a="a"></a>')

        self.tag.removeAttribute('a')
        self.check_noattr('a')
        self.assertEqual(self.tag.a, '')
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_str_setattr(self):
        self.tag.setAttribute('b', 'b')
        self.check_hasattr('b')
        self.assertEqual(self.tag.b, 'b')
        self.assertEqual(self.tag.getAttribute('b'), 'b')
        self.assertEqual(self.tag.html, '<a b="b"></a>')

        del self.tag.b
        self.check_noattr('b')
        self.assertEqual(self.tag.b, '')
        self.assertEqual(self.tag.html, '<a></a>')
        # delete again, but not raise error
        del self.tag.b

    def test_special_attr_bool(self):
        for attr in ['a', 'b', 'c', 'd', 'e']:
            self.check_noattr(attr)
        self.assertFalse(self.tag.a)
        self.assertFalse(self.tag.b)
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_bool_setter(self):
        self.tag.c = True
        self.check_hasattr('c')
        self.assertTrue(self.tag.c)
        self.assertEqual(self.tag.html, '<a c></a>')

        self.tag.c = False
        self.check_noattr('c')
        self.assertFalse(self.tag.c)
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_bool_setattr(self):
        self.tag.setAttribute('d', 'd')
        self.check_hasattr('d')
        self.assertTrue(self.tag.d)
        self.assertEqual(self.tag.html, '<a d></a>')

        self.tag.removeAttribute('d')
        self.check_noattr('d')
        self.assertFalse(self.tag.d)
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_bool_setattr_empty(self):
        # In this case, 'd' still exists and True (compatible with JS...)
        self.tag.setAttribute('d', '')
        self.check_hasattr('d')
        self.assertEqual(self.tag.html, '<a d></a>')

        # Now remove 'd'
        self.tag.d = ''
        self.check_noattr('d')
        self.assertFalse(self.tag.d)
        self.assertEqual(self.tag.html, '<a></a>')

    def test_special_attr_bool_setattr_false(self):
        # In this case, 'd' still exists and True (compatible with JS...)
        self.tag.setAttribute('d', False)
        self.check_hasattr('d')
        self.assertEqual(self.tag.html, '<a d></a>')

        # Now remove 'd'
        del self.tag.d
        self.check_noattr('d')
        self.assertFalse(self.tag.d)
        self.assertEqual(self.tag.html, '<a></a>')


class TestElement(TestCase):
    def setUp(self):
        customElements.clear()
        self.elm = Element('tag')
        self.c1 = Element('c1')
        self.c2 = Element('c2')
        self.c1.classList.add('c1')
        self.c2.classList.add('c2')

    def tearDown(self):
        del self.elm
        del self.c1
        del self.c2
        super().tearDown()

    def test_constructor(self):
        elm = Element('a')
        self.assertEqual(elm.nodeName, 'A')
        self.assertEqual(elm.tagName, 'A')
        self.assertEqual(elm.localName, 'a')

        self.assertFalse(elm.hasChildNodes())
        self.assertFalse(elm.hasAttributes())

    def test_init_parent(self):
        elm = Element('a', parent=self.elm)
        self.assertIs(elm.parentNode, self.elm)

    def test_init_attrs(self):
        elm = Element('a', src='b', href='c')
        self.assertFalse(elm.hasChildNodes())
        self.assertTrue(elm.hasAttributes())
        self.assertTrue(elm.getAttribute('src'), 'b')
        self.assertTrue(elm.getAttribute('href'), 'c')

    def test_attrs(self):
        self.assertFalse(self.elm.hasAttributes())
        self.assertFalse(self.elm.hasAttribute('src'))
        self.assertNotIn('src', self.elm.attributes)
        self.assertIsNone(self.elm.getAttribute('src'))
        self.assertEqual(self.elm.html, '<tag></tag>')
        self.elm.setAttribute('src', 'a')
        self.assertTrue(self.elm.hasAttributes())
        self.assertTrue(self.elm.hasAttribute('src'))
        self.assertIn('src', self.elm.attributes)
        self.assertEqual(self.elm.getAttribute('src'), 'a')
        self.assertEqual(self.elm.html, '<tag src="a"></tag>')

        self.elm.removeAttribute('src')
        self.assertFalse(self.elm.hasAttributes())
        self.assertFalse(self.elm.hasAttribute('src'))
        self.assertNotIn('src', self.elm.attributes)
        self.assertIsNone(self.elm.getAttribute('src'))
        self.assertEqual(self.elm.html, '<tag></tag>')

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
        self.assertEqual(self.elm.firstChild.tag, 'b')
        self.assertTrue(isinstance(self.elm.firstChild, HTMLElement))

    def test_inner_html_nest(self):
        html = '<b><c>d</c>e</b>'
        self.elm.innerHTML = html
        self.assertEqual(self.elm.innerHTML, html)
        self.assertEqual(self.elm.firstChild.html, html)
        self.assertEqual(self.elm.firstChild.firstChild.html, '<c>d</c>')
        self.assertEqual(self.elm.firstChild.firstChild.innerHTML, 'd')
        self.assertEqual(self.elm.firstChild.lastChild.html, 'e')
        self.assertTrue(isinstance(self.elm.firstChild.lastChild, Text))

    def test_parse_html_text(self):
        html = '''
        <a>a1</a1>
        b
        '''
        self.elm.innerHTML = html
        # fisrt node is empty (\n+spaces) text node
        self.assertEqual(self.elm.childNodes.length, 3)
        self.assertTrue(isinstance(self.elm.firstChild, Text))
        self.assertTrue(isinstance(self.elm.lastChild, Text))
        self.assertTrue(isinstance(self.elm.firstElementChild, HTMLElement))
        self.assertTrue(isinstance(self.elm.lastElementChild, HTMLElement))

    def test_insert_adjacent_html(self):
        self.elm.appendChild(self.c1)
        self.c1.insertAdjacentHTML('beforebegin', '<a></a>')
        self.assertEqual(self.elm.childNodes.length, 2)
        self.assertIs(self.elm.lastElementChild, self.c1)
        self.c1.insertAdjacentHTML('afterend', 'text')
        self.assertEqual(self.elm.childNodes.length, 3)
        self.assertIs(self.elm.lastElementChild, self.c1)
        self.c1.insertAdjacentHTML('afterBegin', '<b></b>')
        self.assertEqual(self.c1.childNodes.length, 1)
        self.c1.insertAdjacentHTML('BeforeEnd', '<c></c>')
        self.assertEqual(self.c1.childNodes.length, 2)
        with self.assertRaises(ValueError):
            self.c1.insertAdjacentHTML('a', 'b')

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
        elm = Element('a', class_='a')
        self.assertEqual(elm.html, '<a class="a"></a>')
        self.assertEqual(elm.classList.length, 1)
        self.assertIn('a', elm.classList)

        elm2 = Element('a', **{'class': 'b'})
        self.assertEqual(elm2.html, '<a class="b"></a>')
        self.assertEqual(elm2.classList.length, 1)
        self.assertIn('b', elm2.classList)

    def test_init_class_multi_str(self):
        elm = Element('a', class_='a1 a2')
        self.assertEqual(elm.html, '<a class="a1 a2"></a>')
        self.assertEqual(elm.classList.length, 2)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertNotIn('a1 a2', elm.classList)

    def test_init_class_multi_list(self):
        elm = Element('a', class_=['a1', 'a2'])
        self.assertEqual(elm.html, '<a class="a1 a2"></a>')
        self.assertEqual(elm.classList.length, 2)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertNotIn('a1 a2', elm.classList)

    def test_init_class_multi_mixed(self):
        elm = Element('a', class_=['a1', 'a2 a3'])
        self.assertEqual(elm.html, '<a class="a1 a2 a3"></a>')
        self.assertEqual(elm.classList.length, 3)
        self.assertIn('a1', elm.classList)
        self.assertIn('a2', elm.classList)
        self.assertIn('a3', elm.classList)
        self.assertNotIn('a2 a3', elm.classList)

    def test_reference(self):
        gc.collect()
        elm = Element('a')
        _id = id(elm)
        self.assertIn(elm, Element._elements)
        del elm
        gc.collect()  # run gc
        for elm in Element._elements:
            assert id(elm) != _id

    def test_reference_with_id(self):
        gc.collect()
        elm = Element('a', id='a')
        _id = id(elm)
        self.assertIn(elm.id, Element._elements_with_id)
        del elm
        gc.collect()
        self.assertNotIn('a', Element._elements_with_id)
        for elm in Element._elements:
            assert id(elm) != _id

    def test_reference_add_id(self):
        gc.collect()
        elm = Element('a')
        _id = id(elm)
        self.assertNotIn(elm, Element._elements_with_id.values())
        elm.id = 'a'
        self.assertIn('a', Element._elements_with_id)
        self.assertIn(elm, Element._elements_with_id.values())
        elm.id = 'b'
        self.assertNotIn('a', Element._elements_with_id)
        self.assertIn('b', Element._elements_with_id)
        self.assertIn(elm, Element._elements_with_id.values())
        elm.setAttribute('id', 'c')
        self.assertNotIn('b', Element._elements_with_id)
        self.assertIn('c', Element._elements_with_id)
        self.assertIn(elm, Element._elements_with_id.values())
        del elm
        gc.collect()
        self.assertNotIn('c', Element._elements_with_id)
        for elm in Element._elements:
            assert id(elm) != _id

    def test_reference_del_id(self):
        gc.collect()
        elm = Element('a', id='a')
        self.assertIn('a', Element._elements_with_id)
        self.assertIn(elm, Element._elements_with_id.values())
        elm.removeAttribute('id')
        self.assertNotIn('a', Element._elements_with_id)
        self.assertNotIn(elm, Element._elements_with_id.values())

    def test_is_attr(self):
        '''``is`` is a reserved word for python, so use ``is_`` in constructor.
        '''
        elm = Element('tag', is_='elm')
        self.assertIn('is', elm.attributes)
        self.assertNotIn('is_', elm.attributes)
        self.assertEqual('elm', elm.getAttribute('is'))
        self.assertIsNone(elm.getAttribute('is_'))

        # ``is_`` is not treated as special at setAttribute
        elm.setAttribute('is_', 'new')
        self.assertEqual('elm', elm.getAttribute('is'))
        self.assertEqual('new', elm.getAttribute('is_'))

    class NewTag(HTMLElement):
        pass

    def test_custom_tag(self):
        self.elm.innerHTML = '<new-tag></new-tag>'
        child = self.elm.firstChild
        self.assertEqual(child.__class__, HTMLElement)
        customElements.define('new-tag', self.NewTag)
        self.assertEqual(child.__class__, self.NewTag)

    def test_custom_tag_registered(self):
        customElements.define('new-tag', self.NewTag)
        self.elm.innerHTML = '<new-tag></new-tag>'
        self.assertEqual(self.elm.firstChild.__class__, self.NewTag)

    def test_custom_tag_is(self):
        self.elm.innerHTML = '<a is="my-a"></a>'
        child = self.elm.firstChild
        self.assertEqual(child.__class__, HTMLElement)
        self.assertEqual(child.getAttribute('is'), 'my-a')
        customElements.define('my-a', self.NewTag, {'extends': 'a'})
        self.assertEqual(self.elm.firstChild.__class__, self.NewTag)

    def test_custom_tag_is_registered(self):
        customElements.define('my-a', self.NewTag, {'extends': 'a'})
        self.elm.innerHTML = '<a is="my-a"></a>'
        self.assertEqual(self.elm.firstChild.__class__, self.NewTag)

    def test_invalid_define_args(self):
        with self.assertRaises(TypeError):
            customElements.define(1, 2, 3)


class TestHTMLElement(TestCase):
    def setUp(self):
        self.elm = HTMLElement('a')

    def test_attrs_bool(self):
        self.assertFalse(self.elm.hasAttribute('hidden'))
        self.assertNotIn('hidden', self.elm.attributes)
        self.assertIsNone(self.elm.getAttribute('hidden'))
        self.elm.setAttribute('hidden', True)

        self.assertTrue(self.elm.hasAttributes())
        self.assertTrue(self.elm.hasAttribute('hidden'))
        self.assertIn('hidden', self.elm.attributes)
        self.assertEqual(self.elm.getAttribute('hidden'), True)
        self.assertEqual(self.elm.html, '<a hidden></a>')

        # This is complatible with JS, but quite confusing
        self.elm.setAttribute('hidden', False)
        self.assertTrue(self.elm.hasAttributes())
        self.assertTrue(self.elm.hasAttribute('hidden'))
        self.assertIn('hidden', self.elm.attributes)
        # In chrome, <a hidden="false">, should we convert to string?
        self.assertFalse(self.elm.getAttribute('hidden'))
        self.assertEqual(self.elm.html, '<a hidden></a>')

        self.elm.hidden = False
        self.assertFalse(self.elm.hasAttribute('hidden'))
        self.assertNotIn('hidden', self.elm.attributes)
        self.assertIsNone(self.elm.getAttribute('hidden'))
        self.assertEqual(self.elm.html, '<a></a>')

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

    def test_type(self):
        n = HTMLElement('input')
        n.type = 'text'
        self.assertEqual(n.start_tag, '<input type="text">')

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

    @skipIf(sys.version_info < (3, 5), 'py34 does not keep style order')
    def test_style_setter(self):
        self.elm.style = 'color: red;'
        self.assertEqual(self.elm.style.cssText, 'color: red;')
        self.assertEqual(self.elm.getAttribute('style'), 'color: red;')
        self.assertEqual(self.elm.html, '<a style="color: red;"></a>')

        self.elm.style.color = 'black'
        self.elm.style.background = 'red'
        # py34 does not keep style order
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

    def test_attr_clone(self):
        self.elm.draggable = True
        self.elm.hidden = True
        clone = self.elm.cloneNode()
        self.assertEqual(clone.html, '<a draggable hidden></a>')
        self.elm.hidden = False
        self.assertEqual(clone.html, '<a draggable hidden></a>')
        clone.draggable = False
        self.assertEqual(self.elm.html, '<a draggable></a>')
        self.assertEqual(clone.html, '<a hidden></a>')

    def test_attr_clone_deep(self):
        self.elm.draggable = True
        self.elm.hidden = True
        clone = self.elm.cloneNode(deep=True)
        self.assertEqual(clone.html, '<a draggable hidden></a>')
        self.elm.hidden = False
        self.assertEqual(clone.html, '<a draggable hidden></a>')
        clone.draggable = False
        self.assertEqual(self.elm.html, '<a draggable></a>')
        self.assertEqual(clone.html, '<a hidden></a>')


class TestSelectElement(TestCase):
    def setUp(self):
        self.select = HTMLSelectElement('select')
        self.opt1 = HTMLOptionElement('option')
        self.opt2 = HTMLOptionElement('option')
        self.opt3 = HTMLOptionElement('option')

    def test_options(self) -> None:
        self.assertEqual(self.select.length, 0)
        self.assertEqual(self.select.options.length, 0)
        self.select.append(self.opt1)
        self.assertEqual(self.select.length, 1)
        self.assertEqual(self.select.options.length, 1)
        self.select.append(self.opt2, self.opt3)
        self.assertEqual(self.select.length, 3)
        self.assertEqual(self.select.options.length, 3)

    def test_selected(self) -> None:
        self.select.append(self.opt1, self.opt2, self.opt3)
        for opt in self.select.options:
            self.assertFalse(opt.selected)
        self.assertEqual(self.select.selectedOptions.length, 0)
        self.opt1.selected = True
        self.assertEqual(self.select.selectedOptions.length, 1)
        self.opt2.selected = True
        self.assertEqual(self.select.selectedOptions.length, 2)
        self.opt3.selected = True
        self.assertEqual(self.select.selectedOptions.length, 3)
        self.opt1.selected = False
        self.assertEqual(self.select.selectedOptions.length, 2)
