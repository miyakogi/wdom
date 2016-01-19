#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import pytest
from wdom.dom import TextNode, Dom, HtmlDom, PyNode, Node
from wdom.dom import ClassList, EventListener
from wdom.dom import NewNodeClass


class TestTextNode(object):
    def setup(self):
        self.text_node = TextNode('text')

    def test_html(self):
        assert TextNode('text').html == 'text'

    def test_html_escape(self):
        assert TextNode('<').html == '&lt;'
        assert TextNode('>').html == '&gt;'
        assert TextNode('&').html == '&amp;'
        assert TextNode('"').html == '&quot;'
        assert TextNode('\'').html == '&#x27;'


class TestDom(object):
    '''Test for Basic Dom implementation'''
    def setup(self):
        self.dom = Dom()
        self.c1 = Dom(c="1")
        self.c2 = Dom(c="2")

    def test_name(self):
        assert self.dom.tag == 'tag'
        assert self.dom.tagName == 'TAG'
        assert self.dom.localName == 'tag'

        class A(Dom):
            tag = 'Atag'
        a = A()
        assert a.tag == 'Atag'
        assert a.tagName == 'ATAG'
        assert a.localName == 'atag'

    def test_tag_string(self):
        assert '<tag></tag>' == self.dom.html

    def test_attr_init(self):
        dom = Dom(attrs={'src': 'a'})
        assert '<tag src="a"></tag>' == dom.html
        dom.removeAttribute('src')
        assert '<tag></tag>' == dom.html

    def test_attr_atomic(self):
        # test add tag-attr
        self.dom['a'] = 'b'
        assert self.dom['a'] == 'b'
        assert 'a="b"' in self.dom.html
        assert '<tag a="b">' == self.dom.start_tag()
        assert '<tag a="b"></tag>' == self.dom.html
        del self.dom['a']
        assert '<tag></tag>' == self.dom.html

    def test_attr_addremove(self):
        assert self.dom.hasAttributes() is False
        assert self.dom.hasAttribute('a') is False
        self.dom.setAttribute('a', 'b')
        assert self.dom.hasAttributes() is True
        assert self.dom.hasAttribute('a') is True
        assert self.dom.hasAttribute('b') is False
        assert 'b' == self.dom.getAttribute('a')
        assert '<tag a="b"></tag>' == self.dom.html
        assert self.dom.attributes == {'a': 'b'}
        self.dom.removeAttribute('a')
        assert self.dom.hasAttributes() is False
        assert '<tag></tag>' == self.dom.html
        assert self.dom.attributes == {}

        assert self.dom.getAttribute('aaaa') is None

    def test_attr_multi(self):
        self.dom.setAttribute('c', 'd')
        self.dom.setAttribute('e', 'f')
        assert 'c="d"' in self.dom.html
        assert 'e="f"' in self.dom.html

    def test_attr_overwrite(self):
        self.dom.setAttribute('c', 'd')
        self.dom.setAttribute('e', 'f')
        self.dom.setAttribute('c', 'new_d')
        assert 'c="d"' not in self.dom.html
        assert 'c="new_d"' in self.dom.html
        assert 'e="f"' in self.dom.html

    def test_child_addremove(self):
        assert not self.dom.hasChildNodes()
        self.dom.appendChild(self.c1)
        assert self.dom.hasChildNodes()
        assert '<tag><tag c="1"></tag></tag>' == self.dom.html
        assert self.c1 in self.dom
        self.dom.removeChild(self.c1)
        assert not self.dom.hasChildNodes()
        assert self.c1 not in self.dom
        assert '<tag></tag>' == self.dom.html

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
        assert self.dom.firstChild is None
        assert self.dom.lastChild is None
        self.dom.appendChild(self.c1)
        assert self.dom.firstChild is self.c1
        assert self.dom.lastChild is self.c1
        self.dom.appendChild(self.c2)
        assert self.dom.firstChild is self.c1
        assert self.dom.lastChild is self.c2

    def test_child_deep(self):
        self.dom.appendChild(self.c1)
        self.c1.appendChild(self.c2)
        assert self.c2 not in self.dom
        assert self.c2 in self.c1
        assert '<tag><tag c="1"><tag c="2"></tag></tag></tag>' == self.dom.html

    def test_child_nodes(self):
        self.dom.appendChild(self.c1)
        self.dom.appendChild(self.c2)
        assert len(self.dom.childNodes) == 2
        assert self.dom.childNodes[0] is self.c1
        assert self.dom.childNodes[1] is self.c2

    def test_child_replace(self):
        self.dom.append(self.c1)
        assert self.c1 in self.dom
        assert self.c2 not in self.dom
        assert '<tag><tag c="1"></tag></tag>' == self.dom.html
        self.dom.replaceChild(self.c2, self.c1)
        assert self.c1 not in self.dom
        assert self.c2 in self.dom
        assert '<tag><tag c="2"></tag></tag>' == self.dom.html

    def test_text_addremove(self):
        self.dom.textContent = 'text'
        assert self.dom.hasChildNodes() is True
        assert '<tag>text</tag>' == self.dom.html
        assert 'text' in self.dom
        assert self.dom[0].parent == self.dom

        self.dom.textContent = ''
        assert self.dom.hasChildNodes() is False
        assert '<tag></tag>' == self.dom.html

    def test_textcontent(self):
        assert self.dom.textContent == ''
        self.dom.textContent = 'a'
        assert self.dom.textContent == 'a'
        assert '<tag>a</tag>' == self.dom.html
        self.dom.textContent = 'b'
        assert self.dom.textContent == 'b'
        assert '<tag>b</tag>' == self.dom.html

    def test_textcontent_child(self):
        self.dom.textContent = 'a'
        self.dom.appendChild(self.c1)
        assert '<tag>a<tag c="1"></tag></tag>' == self.dom.html
        self.c1.textContent = 'c1'
        assert '<tag>a<tag c="1">c1</tag></tag>' == self.dom.html
        assert 'ac1' == self.dom.textContent
        self.dom.textContent = 'b'
        assert '<tag>b</tag>' == self.dom.html
        assert self.c1.parentNode is None

    def test_closing_tag(self):
        class Img(Dom):
            tag = 'img'
        img = Img()
        assert '<img>' == img.html
        img.setAttribute('src', 'a')
        assert '<img src="a">' == img.html

    def _test_shallow_copy(self, clone):
        assert self.dom.hasChildNodes() is True
        assert clone.hasChildNodes() is False
        assert len(clone) == 0
        assert '<tag src="a"></tag>' == clone.html

        assert clone.hasAttributes() is True
        assert clone.getAttribute('src') == 'a'
        clone.setAttribute('src', 'b')
        assert clone.getAttribute('src') == 'b'
        assert self.dom.getAttribute('src') == 'a'

        clone.append(self.c2)
        assert clone.hasChildNodes() is True
        assert self.c2 in clone
        assert self.c2 not in self.dom

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
        assert clone.hasChildNodes() is True
        assert len(clone) == 1
        assert self.c1 in self.dom
        assert self.c1 not in clone

        self.c1.setAttribute('src', 'b')
        assert self.c1.getAttribute('src') == 'b'
        assert clone[0].getAttribute('src') is None

        clone.append(self.c2)
        assert len(clone) == 2
        assert len(self.dom) == 1

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
        assert self.dom.previousSibling is None
        assert self.dom.nextSibling is None
        assert self.c1.previousSibling is None
        assert self.c2.previousSibling is self.c1
        assert self.c1.nextSibling is self.c2
        assert self.c2.nextSibling is None

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
        assert len(a_list) == 2
        assert a_list[0] is a1
        assert a_list[1] is a2

        b_list = self.dom.getElementsByTagName('b')
        assert len(b_list) == 2
        assert b_list[0] is b1
        assert b_list[1] is b2

        b_sub_list = b1.getElementsByTagName('b')
        assert len(b_sub_list) == 1
        assert b_sub_list[0] is b2


class TestClassList(object):
    def setup(self):
        self.cl = ClassList()

    def test_addremove(self):
        assert bool(self.cl) is False
        assert len(self.cl) == 0
        self.cl.append('a')
        assert bool(self.cl) is True
        assert len(self.cl) == 1
        assert 'a' in self.cl
        assert 'a' == self.cl.to_string()
        self.cl.append('b')
        assert bool(self.cl) is True
        assert len(self.cl) == 2
        assert 'a' in self.cl
        assert 'b' in self.cl
        assert 'a b' == self.cl.to_string()
        self.cl.remove('a')
        assert bool(self.cl) is True
        assert len(self.cl) == 1
        assert 'a' not in self.cl
        assert 'b' in self.cl
        assert 'b' == self.cl.to_string()

    def test_add_multi_string(self):
        self.cl.append('a b')
        assert len(self.cl) == 2
        assert 'a b' == self.cl.to_string()
        self.cl.remove('a')
        assert len(self.cl) == 1
        assert 'b' == self.cl.to_string()

    def test_add_multi_list(self):
        self.cl.append(['a', 'b'])
        assert len(self.cl) == 2
        assert 'a b' == self.cl.to_string()
        self.cl.remove('a')
        assert len(self.cl) == 1
        assert 'b' == self.cl.to_string()

    def test_add_multi_mixed(self):
        self.cl.append(['a', 'b c'])
        assert len(self.cl) == 3
        assert 'a b c' == self.cl.to_string()
        self.cl.remove('b')
        assert len(self.cl) == 2
        assert 'a c' == self.cl.to_string()

    def test_add_none(self):
        self.cl.append(None)
        assert len(self.cl) == 0
        assert bool(self.cl) is False
        assert '' == self.cl.to_string()

    def test_add_blank(self):
        self.cl.append('')
        assert len(self.cl) == 0
        assert bool(self.cl) is False
        assert '' == self.cl.to_string()

    def test_add_invlalid(self):
        with pytest.raises(TypeError):
            self.cl.append(1)
        with pytest.raises(TypeError):
            self.cl.append(Dom())
        assert len(self.cl) == 0
        assert bool(self.cl) is False
        assert '' == self.cl.to_string()

    def test_iter(self):
        cls = ['a', 'b', 'c']
        self.cl.append(cls)
        for c in self.cl:
            assert c in cls
            cls.remove(c)
        assert len(cls) == 0

    def test_reverse(self):
        self.cl.append('a b c d')
        self.cl.reverse()
        assert 'd c b a' == self.cl.to_string()


class TestHtmlDom(object):
    def setup(self):
        self.dom = HtmlDom()
        self.c1 = HtmlDom()
        self.c2 = HtmlDom()

    def test_class_addremove(self):
        assert self.dom.hasClasses() is False
        assert self.dom.hasClass('a') is False
        assert '<html-tag></html-tag>' == self.dom.html
        self.dom.addClass('a')
        assert self.dom.hasClasses() is True
        assert self.dom.hasClass('a') is True
        assert self.dom.hasClass('b') is False
        assert '<html-tag class="a"></html-tag>' == self.dom.html
        self.dom.removeClass('a')
        assert self.dom.hasClasses() is False
        assert self.dom.hasClass('a') is False
        assert '<html-tag></html-tag>' == self.dom.html

    def test_class_in_init(self) -> None:
        dom = HtmlDom(class_ = 'a')
        assert dom.hasClass('a') is True
        assert dom.hasClasses() is True
        assert '<html-tag class="a"></html-tag>' == dom.html
        dom.removeClass('a')
        assert dom.hasClass('a') is False
        assert dom.hasClasses() is False
        assert '<html-tag></html-tag>' == dom.html

    def test_class_addremove_multi_string(self):
        self.dom.addClass('a b')
        assert self.dom.hasClasses() is True
        assert self.dom.hasClass('a') is True
        assert self.dom.hasClass('b') is True
        assert '<html-tag class="a b"></html-tag>' == self.dom.html
        self.dom.removeClass('a')
        assert self.dom.hasClasses() is True
        assert self.dom.hasClass('a') is False
        assert self.dom.hasClass('b') is True
        assert '<html-tag class="b"></html-tag>' == self.dom.html

    def test_class_addremove_multi_list(self):
        self.dom.addClass(['a', 'b'])
        assert self.dom.hasClasses() is True
        assert self.dom.hasClass('a') is True
        assert self.dom.hasClass('b') is True
        assert '<html-tag class="a b"></html-tag>' == self.dom.html
        self.dom.removeClass('a')
        assert self.dom.hasClasses() is True
        assert self.dom.hasClass('a') is False
        assert self.dom.hasClass('b') is True
        assert '<html-tag class="b"></html-tag>' == self.dom.html

    def test_class_getset(self) -> None:
        assert self.dom['class'] == ''
        self.dom.addClass('a')
        assert self.dom['class'] == 'a'
        self.dom['class'] = 'b'
        assert self.dom['class'] == 'b'
        assert self.dom.hasClass('a') is False
        assert self.dom.hasClass('b') is True

    def test_type_class(self) -> None:
        class A(HtmlDom):
            tag = 'input'
            type_ = 'button'
        a = A()
        assert '<input type="button">' == a.html

    def test_type_init(self) -> None:
        a = HtmlDom(type='button')
        assert '<html-tag type="button"></html-tag>' == a.html

    def test_type_attr(self) -> None:
        a = HtmlDom()
        a.setAttribute('type', 'checkbox')
        assert '<html-tag type="checkbox"></html-tag>' == a.html

    def test_hidden(self):
        self.dom.show()
        assert '<html-tag></html-tag>' == self.dom.html
        self.dom.hide()
        assert '<html-tag hidden></html-tag>' == self.dom.html
        self.dom.show()
        assert '<html-tag></html-tag>' == self.dom.html

    def test_clone_node_sharrow_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        clone = self.dom.cloneNode()
        assert '<html-tag class="a"></html-tag>' == clone.html

        clone.removeClass('a')
        assert '<html-tag></html-tag>' == clone.html
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == self.dom.html

        clone.addClass('b')
        assert '<html-tag class="b"></html-tag>' == clone.html
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == self.dom.html

    def test_clone_node_sharrow_hidden(self):
        self.dom.hide()
        clone = self.dom.cloneNode()
        assert '<html-tag hidden></html-tag>' == clone.html
        clone.show()
        assert '<html-tag hidden></html-tag>' == self.dom.html
        assert '<html-tag></html-tag>' == clone.html

    def test_clone_node_deep_class(self):
        self.dom.appendChild(self.c1)
        self.dom.addClass('a')
        self.c1.addClass('b')
        clone = self.dom.cloneNode(deep=True)
        assert '<html-tag class="a"><html-tag class="b"></html-tag></html-tag>' == self.dom.html
        assert '<html-tag class="a"><html-tag class="b"></html-tag></html-tag>' == clone.html

        clone.children[0].removeClass('b')
        assert '<html-tag class="a"><html-tag class="b"></html-tag></html-tag>' == self.dom.html
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == clone.html

        self.c1.removeClass('b')
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == self.dom.html
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == clone.html

        clone.addClass('c')
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == self.dom.html
        assert '<html-tag class="a c"><html-tag></html-tag></html-tag>' == clone.html

        clone.removeClass('a')
        assert '<html-tag class="a"><html-tag></html-tag></html-tag>' == self.dom.html
        assert '<html-tag class="c"><html-tag></html-tag></html-tag>' == clone.html

    def test_clone_node_deep_hidden(self):
        self.dom.appendChild(self.c1)
        self.c1.hide()
        clone = self.dom.cloneNode(deep=True)
        assert '<html-tag><html-tag hidden></html-tag></html-tag>' == self.dom.html
        assert '<html-tag><html-tag hidden></html-tag></html-tag>' == clone.html

        self.c1.show()
        assert '<html-tag><html-tag></html-tag></html-tag>' == self.dom.html
        assert '<html-tag><html-tag hidden></html-tag></html-tag>' == clone.html

    def test_classes_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1'
        assert A.get_class_list().to_string() == 'a1'
        a = A()
        assert '<a class="a1"></a>' == a.html
        a.addClass('a2')
        assert '<a class="a1 a2"></a>' == a.html
        with pytest.raises(ValueError):
            a.removeClass('a1')
        assert '<a class="a1 a2"></a>' == a.html

    def test_classes_multiclass(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'
        assert A.get_class_list().to_string() == 'a1 a2'
        a = A()
        a.addClass('a3 a4')
        assert '<a class="a1 a2 a3 a4"></a>' == a.html

    def test_classes_inherit_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'

        assert B.get_class_list().to_string() == 'a1 a2 b1 b2'
        b = B()
        b.addClass('b3')
        assert '<b class="a1 a2 b1 b2 b3"></b>' == b.html

    def test_classes_notinherit_class(self):
        class A(HtmlDom):
            tag = 'a'
            class_ = 'a1 a2'

        class B(A):
            tag = 'b'
            class_ = 'b1 b2'
            inherit_class = False

        assert B.get_class_list().to_string() == 'b1 b2'
        b = B()
        b.addClass('b3')
        assert '<b class="b1 b2 b3"></b>' == b.html

        class C(B):
            tag = 'c'
            class_ = 'c1 c2'
        assert C.get_class_list().to_string() == 'b1 b2 c1 c2'


class TestPyNode(object):
    def test_id_rand(self):
        dom = PyNode()
        assert re.match(r'<py-node id="\d+"></py-node>', dom.html)

    def test_id_constructor(self):
        dom = PyNode(id='test')
        assert '<py-node id="test"></py-node>' == dom.html


class TestEventListener(object):
    # To be implemented
    EventListener


class TestNode(object):
    def setup(self):
        self.dom = Node()

    def test_event_addremove(self):
        listener = lambda data: None
        listener_2 = lambda data: None
        self.dom.addEventListener('click', listener)
        assert re.match(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        )
        # Add listner on same type. one event should be defined in html.
        self.dom.addEventListener('click', listener_2)
        assert re.match(
            r'<node id="\d+" onclick="W.onclick\(this\);"></node>',
            self.dom.html
        )

        # Add defferent event type. two event shoud be defined in html.
        self.dom.addEventListener('change', listener)
        assert 'onchange="W.onchange(this);"' in self.dom.html
        assert 'onclick="W.onclick(this);"' in self.dom.html

        # Remove one listener and no listener is define for the event.
        # Only one event shoud be in html.
        self.dom.removeEventListener('change', listener)
        assert 'onchange="W.onchange(this);"' not in self.dom.html
        assert 'onclick="W.onclick(this);"' in self.dom.html

        # Remove one listener but still have a listener for the event.
        # The event shoud be still define in html.
        self.dom.removeEventListener('click', listener)
        assert 'onclick="W.onclick(this);"' in self.dom.html

        # Remove one more listener and have no listener for the event.
        # No event shoud be still define in html.
        self.dom.removeEventListener('click', listener_2)
        assert re.match(r'<node id="\d+"></node>', self.dom.html)


class TestNewClass(object):
    def test_create(self):
        MyTag = NewNodeClass('MyTag', 'mt')
        assert issubclass(MyTag, Node)
        assert MyTag.__name__ == 'MyTag'
        assert MyTag.tag == 'mt'
        elm = MyTag()
        assert elm.localName == 'mt'
        assert re.match(r'<mt id="\d+"></mt>', elm.html)

    def test_create_by_classname(self):
        MyTag = NewNodeClass('MyTag')
        assert issubclass(MyTag, Node)
        assert MyTag.__name__ == 'MyTag'
        assert MyTag.tag == 'mytag'
        elm = MyTag()
        assert re.match(r'<mytag id="\d+"></mytag>', elm.html)

    def test_create_class_with_baseclass(self):
        MyTag = NewNodeClass('MyTag', 'mt')
        MyTag2 = NewNodeClass('MyTag2', 'mt2', MyTag)
        assert issubclass(MyTag2, MyTag)
        assert MyTag2.tag == 'mt2'
        elm = MyTag2()
        assert re.match(r'<mt2 id="\d+"></mt2>', elm.html)

        class A(object):
            pass
        MyTag3 = NewNodeClass('MyTag3', 'mt3', (MyTag, A))
        assert issubclass(MyTag3, MyTag)
        assert issubclass(MyTag3, A)

    def test_closing_tag(self):
        Img = NewNodeClass('Img')
        img = Img()
        assert img.html == '<img id="{}">'.format(img.id)
        img = Img(src='/image.jpg')
        assert img.html == '<img src="/image.jpg" id="{}">'.format(img.id)

    def test_create_class_with_class_attr(self):
        MyTag = NewNodeClass('MyTag', 'mt', class_='for test')
        elm = MyTag()
        assert elm.html == '<mt class="for test" id="{}"></mt>'.format(elm.id)
        elm2 = MyTag()
        elm2.addClass('new class')
        assert elm2.html == '<mt class="for test new class" id="{}"></mt>'.format(str(id(elm2)))
