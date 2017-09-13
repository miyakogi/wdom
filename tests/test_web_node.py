#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import MagicMock, call

from syncer import sync

from wdom.document import set_app
from wdom.event import create_event
from wdom.node import Text
from wdom.server import _tornado
from wdom.web_node import WdomElement

from .base import TestCase


class TestWdomElement(TestCase):
    def setUp(self):
        super().setUp()
        self.elm = WdomElement('tag')
        set_app(self.elm)
        self.c1 = WdomElement()
        self.c2 = WdomElement()
        self.js_mock = MagicMock()
        self.js_mock1 = MagicMock()
        self.js_mock2 = MagicMock()
        self.elm.js_exec = self.js_mock
        self.c1.js_exec = self.js_mock1
        self.c2.js_exec = self.js_mock2
        self.conn_mock = MagicMock()
        _tornado.connections.append(self.conn_mock)

    def tearDown(self):
        _tornado.connections.remove(self.conn_mock)

    def test_id(self):
        self.assertRegex(self.elm.html, r'<tag wdom_id="\d+"></tag>')
        self.assertRegex(self.elm.wdom_id, r'\d+')

    def test_noid(self):
        self.assertEqual('<tag></tag>', self.elm.html_noid)

        self.c1.tag = 'c1'
        appended_child1 = self.elm.appendChild(self.c1)
        self.assertIs(appended_child1, self.c1)
        self.assertEqual('<tag><c1></c1></tag>', self.elm.html_noid)

        self.c2.tag = 'c2'
        appended_child2 = self.c1.appendChild(self.c2)
        self.assertIs(appended_child2, self.c2)
        self.assertEqual('<tag><c1><c2></c2></c1></tag>', self.elm.html_noid)

    def test_id_init(self):
        elm = WdomElement('tag', wdom_id='myid')
        self.assertEqual('<tag wdom_id="myid"></tag>', elm.html)

    def test_connected(self):
        self.assertTrue(self.elm.connected)

    def test_parent(self):
        self.assertTrue(self.elm.parentNode)
        self.assertIsNone(self.c1.parentNode)
        self.elm.appendChild(self.c1)
        self.assertIs(self.elm, self.c1.parentNode)
        self.js_mock1.assert_not_called()
        self.assertEqual(self.js_mock.call_count, 1)
        self.js_mock.assert_called_once_with(
            'insertAdjacentHTML', 'beforeend', self.c1.html)

        removed_child1 = self.elm.removeChild(self.c1)
        self.assertIs(removed_child1, self.c1)
        self.assertIsNone(self.c1.parentNode)
        self.assertEqual(self.js_mock.call_count, 2)
        self.js_mock1.assert_not_called()
        self.js_mock.assert_called_with('removeChildById', self.c1.wdom_id)

    def test_addremove_child(self):
        self.assertFalse(self.elm.hasChildNodes())
        self.elm.appendChild(self.c1)
        self.assertTrue(self.elm.hasChildNodes())
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 1)

        self.elm.insertBefore(self.c2, self.c1)
        self.assertIn(self.c1, self.elm)
        self.assertIn(self.c2, self.elm)
        self.assertEqual(self.elm.length, 2)
        self.c2.remove()
        self.assertEqual(self.elm.length, 1)
        self.assertIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.assertIsNone(self.c2.parentNode)
        self.js_mock2.assert_called_once_with('remove')

        self.elm.removeChild(self.c1)
        self.assertFalse(self.elm.hasChildNodes())
        self.assertEqual(self.elm.length, 0)
        self.assertNotIn(self.c1, self.elm)
        self.assertNotIn(self.c2, self.elm)
        self.js_mock1.assert_called_once_with(
            'insertAdjacentHTML', 'beforebegin', self.c2.html)
        self.assertEqual(self.js_mock.call_count, 3)

        with self.assertRaises(ValueError):
            self.elm.removeChild(self.c1)

    def test_append_text(self):
        from html import escape
        t = '<a>'
        t_node = Text(t)
        self.assertEqual(t_node.textContent, t)
        self.assertEqual(t_node.html, t)
        self.elm.appendChild(t_node)
        self.js_mock.assert_called_once_with(
            'insertAdjacentHTML', 'beforeend', escape('<a>'))
        self.assertEqual(t_node.html, escape(t))

    def test_addremove_attr(self):
        self.elm.setAttribute('src', 'a')
        self.js_mock.assert_called_with('setAttribute', 'src', 'a')
        self.elm.removeAttribute('src')
        self.js_mock.assert_called_with('removeAttribute', 'src')

    def test_attr_subscription(self):
        # test add tag-attr
        self.elm['a'] = 'b'
        self.assertEqual(self.elm['a'], 'b')
        self.assertIn('a="b"', self.elm.html)
        self.assertRegex(self.elm.start_tag, '<tag wdom_id="\d+" a="b">')
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+" a="b"></tag>')
        del self.elm['a']
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+"></tag>')

    def test_style(self):
        self.elm.style = 'color: red;'
        self.js_mock.assert_called_once_with(
            'setAttribute', 'style', 'color: red;')
        self.elm.removeAttribute('style')
        self.js_mock.assert_called_with('removeAttribute', 'style')
        self.elm.style.color = 'black'
        self.js_mock.assert_called_with(
            'setAttribute', 'style', 'color: black;')

    def test_style_init(self):
        _js_exec = WdomElement.js_exec
        WdomElement.js_exec = self.js_mock
        WdomElement('elm', style='color: red;')
        _call = call('setAttribute', 'style', 'color: red;')
        _call_remove = call('removeAttribute', 'style')
        self.js_mock.assert_has_calls([_call])
        count = 0
        for c in self.js_mock.call_args_list:
            if c == _call:
                count += 1
            elif c == _call_remove:
                raise AssertionError('Unexpeted remove style')
        self.assertEqual(count, 1)
        WdomElement.js_exec = _js_exec

    def test_set_text_content(self):
        self.elm.textContent = 'text'
        self.js_mock.assert_called_once_with('textContent', 'text')

    def test_set_inner_html(self):
        self.elm.innerHTML = 'html'
        self.js_mock.assert_called_once_with('innerHTML', 'html')

    def test_shallow_copy(self):
        from copy import copy
        clone = copy(self.elm)
        self.assertNotEqual(clone.wdom_id, self.elm.wdom_id)

        clone = self.elm.cloneNode()
        self.assertNotEqual(clone.wdom_id, self.elm.wdom_id)

    def test_deep_copy(self):
        from copy import deepcopy
        clone = deepcopy(self.elm)
        self.assertNotEqual(clone.wdom_id, self.elm.wdom_id)

        clone = self.elm.cloneNode(deep=True)
        self.assertNotEqual(clone.wdom_id, self.elm.wdom_id)

    def test_click(self):
        mock = MagicMock(_is_coroutine=False)
        self.elm.addEventListener('click', mock)
        self.js_mock.assert_called_once_with('addEventListener', 'click')
        self.elm.click()
        self.js_mock.assert_called_with('click')
        # called only from browser's click event
        self.assertEqual(mock.call_count, 0)

    def test_hidden(self):
        self.elm.show()
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+"></tag>')
        self.elm.hide()
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+" hidden></tag>')
        self.elm.show()
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+"></tag>')

    def test_clone_node_sharrow_hidden(self):
        self.elm.hide()
        clone = self.elm.cloneNode()
        self.assertRegex(clone.html, '<tag wdom_id="\d+" hidden></tag>')
        clone.show()
        self.assertRegex(self.elm.html, '<tag wdom_id="\d+" hidden></tag>')
        self.assertRegex(clone.html, '<tag wdom_id="\d+"></tag>')

    def test_clone_node_deep_hidden(self):
        self.elm.appendChild(self.c1)
        self.c1.tag = 'tag'
        self.c1.hide()
        clone = self.elm.cloneNode(deep=True)
        self.assertRegex(
            self.elm.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" hidden></tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" hidden></tag></tag>',
        )

        self.c1.show()
        self.assertRegex(
            self.elm.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+"></tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+"><tag wdom_id="\d+" hidden></tag></tag>',
        )


class TestWdomElementClass(TestCase):
    def setUp(self):
        super().setUp()
        self.tag = WdomElement('tag')
        self.c1 = WdomElement('tag')
        self.c2 = WdomElement('tag')
        self.conn_mock = MagicMock()
        _tornado.connections.append(self.conn_mock)

    def tearDown(self):
        _tornado.connections.remove(self.conn_mock)

    def test_class_addremove(self):
        self.assertIsFalse(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')
        self.tag.addClass('a')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsTrue(self.tag.hasClass('a'))
        self.assertIsFalse(self.tag.hasClass('b'))
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+" class="a"></tag>')
        self.tag.removeClass('a')
        self.assertIsFalse(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+"></tag>')

    def test_class_in_init(self) -> None:
        tag = WdomElement('tag', class_='a')
        self.assertIsTrue(tag.hasClass('a'))
        self.assertIsTrue(tag.hasClasses())
        self.assertRegex(tag.html, '<tag wdom_id="\d+" class="a"></tag>')
        tag.removeClass('a')
        self.assertIsFalse(tag.hasClass('a'))
        self.assertIsFalse(tag.hasClasses())
        self.assertRegex(tag.html, '<tag wdom_id="\d+"></tag>')

    def test_class_addremove_multi(self):
        self.tag.addClass('a', 'b', 'c')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsTrue(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertIsTrue(self.tag.hasClass('c'))
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a b c"></tag>',
        )
        self.tag.removeClass('a', 'c')
        self.assertIsTrue(self.tag.hasClasses())
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))
        self.assertIsFalse(self.tag.hasClass('c'))
        self.assertRegex(self.tag.html, '<tag wdom_id="\d+" class="b"></tag>')

    def test_class_addremove_multi_string(self):
        with self.assertRaises(ValueError):
            self.tag.addClass('a b')

    def test_class_getset(self) -> None:
        self.assertEqual(self.tag['class'], None)
        self.tag.addClass('a')
        self.assertEqual(self.tag['class'], 'a')
        self.tag['class'] = 'b'
        self.assertEqual(self.tag['class'], 'b')
        self.assertIsFalse(self.tag.hasClass('a'))
        self.assertIsTrue(self.tag.hasClass('b'))

    def test_class_remove_error(self) -> None:
        with self.assertLogs('wdom', 'WARNING'):
            self.tag.removeClass('a')

    def test_clone_node_sharrow_class(self):
        self.tag.appendChild(self.c1)
        self.tag.addClass('a')
        clone = self.tag.cloneNode()
        self.assertRegex(clone.html, '<tag wdom_id="\d+" class="a"></tag>')

        clone.removeClass('a')
        self.assertRegex(clone.html, '<tag wdom_id="\d+"></tag>')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )

        clone.addClass('b')
        self.assertRegex(clone.html, '<tag wdom_id="\d+" class="b"></tag>')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )

    def test_clone_node_deep_class(self):
        self.tag.appendChild(self.c1)
        self.tag.addClass('a')
        self.c1.addClass('b')
        clone = self.tag.cloneNode(deep=True)
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+" class="b">'
            '</tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+" class="b">'
            '</tag></tag>',
        )

        clone.childNodes[0].removeClass('b')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+" class="b">'
            '</tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )

        self.c1.removeClass('b')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )

        clone.addClass('c')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+" class="a c"><tag wdom_id="\d+"></tag></tag>',
        )

        clone.removeClass('a')
        self.assertRegex(
            self.tag.html,
            '<tag wdom_id="\d+" class="a"><tag wdom_id="\d+"></tag></tag>',
        )
        self.assertRegex(
            clone.html,
            '<tag wdom_id="\d+" class="c"><tag wdom_id="\d+"></tag></tag>',
        )

    def test_class_of_class(self):
        class A(WdomElement):
            class_ = 'a1'
        self.assertEqual(A.get_class_list().toString(), 'a1')
        a = A('a')
        self.assertRegex(a.html, '<a wdom_id="\d+" class="a1"></a>')
        a.addClass('a2')
        self.assertRegex(a.html, '<a wdom_id="\d+" class="a1 a2"></a>')
        with self.assertLogs('wdom', 'WARNING'):
            a.removeClass('a1')
        self.assertRegex(a.html, '<a wdom_id="\d+" class="a1 a2"></a>')

    def test_classes_multiclass(self):
        class A(WdomElement):
            class_ = 'a1 a2'
        self.assertEqual(A.get_class_list().toString(), 'a1 a2')
        a = A('a')
        a.addClass('a3', 'a4')
        self.assertRegex(a.html, '<a wdom_id="\d+" class="a1 a2 a3 a4"></a>')

    def test_classes_inherit_class(self):
        class A(WdomElement):
            class_ = 'a1 a2'

        class B(A):
            class_ = 'b1 b2'

        self.assertEqual(B.get_class_list().toString(), 'a1 a2 b1 b2')
        b = B('b')
        b.addClass('b3')
        self.assertRegex(
            b.html,
            '<b wdom_id="\d+" class="a1 a2 b1 b2 b3"></b>',
        )

    def test_classes_notinherit_class(self):
        class A(WdomElement):
            class_ = 'a1 a2'

        class B(A):
            class_ = 'b1 b2'
            inherit_class = False

        self.assertEqual(B.get_class_list().toString(), 'b1 b2')
        b = B('b')
        b.addClass('b3')
        self.assertRegex(b.html, '<b wdom_id="\d+" class="b1 b2 b3"></b>')

        class C(B):
            class_ = 'c1 c2'
        self.assertEqual(C.get_class_list().toString(), 'b1 b2 c1 c2')

    def test_classes_inherit_diamond(self):
        class A(WdomElement):
            class_ = 'a'

        class B(A):
            class_ = 'b'

        class C(A):
            class_ = 'c'

        class D(B, C):
            class_ = 'd'

        self.assertEqual(D.get_class_list().toString(), 'a c b d')


class TestEventMessage(TestCase):
    def setUp(self):
        self.conn_mock = MagicMock()
        _tornado.connections.append(self.conn_mock)
        self.elm = WdomElement('tag')
        set_app(self.elm)
        self.elm.js_exec = MagicMock()
        self.mock = MagicMock(_is_coroutine=False)
        self.elm.addEventListener('click', self.mock)
        msg = {'type': 'click', 'currentTarget': {'id': self.elm.wdom_id}}
        self.event = create_event(msg)

    def tearDown(self):
        _tornado.connections.remove(self.conn_mock)

    def test_handle_event(self):
        self.elm.js_exec.assert_called_once_with('addEventListener', 'click')
        self.elm.dispatchEvent(self.event)
        self.assertTrue(self.mock.called)

    def test_remove_event(self):
        self.elm.removeEventListener('click', self.mock)
        self.elm.js_exec.assert_called_with('removeEventListener', 'click')
        self.elm.dispatchEvent(self.event)
        self.mock.assert_not_called()

    def test_remove_multi_event(self):
        self.elm.addEventListener('click', self.mock)
        self.elm.removeEventListener('click', self.mock)
        with self.assertRaises(AssertionError):
            self.elm.js_exec.assert_has_calls(
                call('removeEventListener', 'click'))
        self.elm.removeEventListener('click', self.mock)
        self.elm.js_exec.assert_called_with('removeEventListener', 'click')
        self.elm.dispatchEvent(self.event)
        self.mock.assert_not_called()


class TestQuery(TestCase):
    def setUp(self):
        super().setUp()
        self.elm = WdomElement('tag')
        set_app(self.elm)
        self.elm.js_exec = MagicMock()
        self.msg = {
            'type': 'response',
            'id': self.elm.wdom_id,
        }
        self.conn_mock = MagicMock()
        _tornado.connections.append(self.conn_mock)

    def tearDown(self):
        _tornado.connections.remove(self.conn_mock)

    def test_query(self):
        fut = self.elm.js_query('test')
        self.elm.js_exec.assert_called_once_with('test', 0)
        self.msg['reqid'] = 0
        self.msg['data'] = 1
        self.elm.on_response(self.msg)
        self.assertEqual(fut.result(), 1)

    @sync
    async def test_scroll(self):
        fut = self.elm.scrollX()
        self.assertFalse(fut.done())
        self.msg['reqid'] = 0
        self.msg['data'] = {'x': 1}
        self.elm.on_response(self.msg)
        x = await fut
        self.assertEqual(x, {'x': 1})
