#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Data binding example
'''

from wdom import server
from wdom.document import set_app, getElementByWdomId
from wdom.themes import Div


def dragstart(e):
    e.dataTransfer.setData('text/plain', e.currentTarget.wdom_id)


def drop(e):
    start_elm = getElementByWdomId(e.dataTransfer.getData('text/plain'))
    current_color = e.currentTarget.style['background-color']
    start_color = start_elm.style['background-color']
    start_elm.style['background-color'] = current_color
    e.currentTarget.style['background-color'] = start_color


class App(Div):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.elm1 = Div(parent=self, draggable=True)
        self.elm1.setAttribute(
            'style',
            'width: 70px; height: 50px; display: inline-block'
        )
        self.elm2 = self.elm1.cloneNode()
        self.elm3 = self.elm1.cloneNode()
        self.elm1.setAttribute('id', '1')
        self.elm2.setAttribute('id', '2')
        self.elm3.setAttribute('id', '3')
        self.append(self.elm2, self.elm3)
        self.elm1.style['background-color'] = 'red'
        self.elm2.style['background-color'] = 'green'
        self.elm3.style['background-color'] = 'blue'
        self.elm1.addEventListener('dragstart', dragstart)
        self.elm2.addEventListener('dragstart', dragstart)
        self.elm3.addEventListener('dragstart', dragstart)
        self.elm1.addEventListener('drop', drop)
        self.elm2.addEventListener('drop', drop)
        self.elm3.addEventListener('drop', drop)

    def update(self, event):
        self.text.textContent = self.textbox.getAttribute('value')


def sample_app(**kwargs):
    return App()


if __name__ == '__main__':
    set_app(sample_app())
    server.start()
