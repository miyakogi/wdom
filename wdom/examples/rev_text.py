#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wdom.event import Event
from wdom.themes import H1


def rev_text(event: Event) -> None:
    elm = event.currentTarget
    elm.textContent = elm.textContent[::-1]


def sample_app(**kwargs) -> H1:
    h1 = H1('Click!')
    h1.addEventListener('click', rev_text)
    return h1


if __name__ == '__main__':
    from wdom.document import set_app
    from wdom import server
    set_app(sample_app())
    server.start()
