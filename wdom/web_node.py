#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from asyncio import coroutine

from wdom.node import HTMLElement, Node
from wdom.webif import WebIF

logger = logging.getLogger(__name__)
js_logger = logger.getChild('ws')
elements = dict()


class WebElement(HTMLElement, WebIF):
    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id:str):
        self._id = id

    def __init__(self, *args, parent=None, **kwargs):
        self.id = kwargs.pop('id', str(id(self)))
        super().__init__(*args, **kwargs)
        elements[self.id] = self
        self.addEventListener('mount', self._on_mount)
        if parent is not None:
            parent.appendChild(self)

    def _get_attrs_by_string(self) -> str:
        attrs_str = ' '.join((super()._get_attrs_by_string(),
                              'id="{}"'.format(self.id)))
        return attrs_str.strip()

    def _on_mount(self, *args, **kwargs):
        for event in self._listeners:
            self._add_event_listener_web(event=event)

    def _remove_web(self):
        self.js_exec('remove')

    def remove(self, *args, **kwargs):
        '''Remove this node from parent's DOM tree.
        '''
        self._remove_web()
        self._remove()

    def _empty_web(self):
        self.js_exec('empty')

    def empty(self):
        self._empty_web()
        self._empty()

    def _append_child_web(self, child: 'WebElement'):
        if isinstance(child, Node):
            html = child.html
        else:
            html = str(child)
        self.js_exec('insertAdjacentHTML', position='beforeend', html=html)

    def appendChild(self, child: 'WebElement') -> Node:
        '''Append child node at the last of child nodes. If this instance is
        connected to the node on browser, the child node is also added to it.
        '''
        self._append_child_web(child)
        return self._append_child(child)

    def _insert_before_web(self, child: 'WebElement', ref_node: 'WebElement'):
        if isinstance(child, WebElement):
            html = child.html
        else:
            html = str(child)

        if isinstance(ref_node, WebElement):
            ref_node.js_exec('insertAdjacentHTML', position='beforebegin',
                                html=html)
        else:
            index = self._children.index(ref_node)
            self.js_exec('insert', index=index, html=html)

    def insertBefore(self, child: 'WebElement', ref_node: 'WebElement') -> Node:
        '''Insert new child node before the reference child node. If the
        reference node is not a child of this node, raise ValueError. If this
        instance is connected to the node on browser, the child node is also
        added to it.
        '''
        self._insert_before_web(child, ref_node)
        return self._insert_before(child, ref_node)

    def _remove_child_web(self, child: 'WebElement'):
        if isinstance(child, WebElement):
            self.js_exec('removeChild', id=child.id)
        else:
            index = self._children.index(child)
            self.js_exec(
                'eval',
                script='node.removeChild(node.childNodes[{}])'.format(index),
            )

    def removeChild(self, child: 'Tag') -> Node:
        '''Remove the child node from this node. If the node is not a child
        of this node, raise ValueError.'''
        self._remove_child_web(child)
        return self._remove_child(child)

    def _replace_child_web(self, new_child, old_child):
        # Does not work... why?
        # self._insert_before_web(new_child, old_child)
        # self._remove_child_web(old_child)
        # This also not work...
        # old_child.js_exec('outerHTML', html=new_child.html)
        self.js_exec('replaceChild', id=old_child.id, html=new_child.html)

    def replaceChild(self, new_child, old_child) -> Node:
        self._replace_child_web(new_child, old_child)
        return self._replace_child(new_child, old_child)

    @coroutine
    def getBoundingClientRect(self):
        fut = yield from self.js_query('getBoundingClientRect')
        return fut

    @property
    def textContent(self) -> str:
        '''Return text contents of this node and all chid nodes. Any value is
        set to this property, all child nodes are removed and new value is set
        as a text node.
        '''
        return self._get_text_content()

    def _set_text_content_web(self, text:str):
        self.js_exec('textContent', text=self.textContent)

    @textContent.setter
    def textContent(self, text: str):
        self._set_text_content(text)
        self._set_text_content_web(text)

    def _set_inner_html_web(self, html:str):
        self.js_exec('innerHTML', html=html)

    @property
    def innerHTML(self) -> str:
        return self._get_inner_html()

    @innerHTML.setter
    def innerHTML(self, html:str):
        self._set_inner_html_web(html)
        self._set_inner_html(html)

    @property
    def html_noid(self) -> str:
        html = self.start_tag.replace(' id="{}"'.format(self.id), '')
        html += ''.join(
            elm.html_noid if isinstance(elm, WebElement) else elm.html
            for elm in self.childNodes
        )
        html += self.end_tag
        return html

    # Window controll
    def scroll(self, x:int, y:int):
        self.js_exec('scroll', x=x, y=y)

    def scrollTo(self, x:int, y:int):
        self.js_exec('scrollTo', x=x, y=y)

    def scrollBy(self, x:int, y:int):
        self.js_exec('scrollBy', x=x, y=y)

    def scrollX(self):
        return self.js_query('scrollX')

    def scrollY(self):
        return self.js_query('scrollY')
