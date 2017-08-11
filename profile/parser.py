#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cProfile import Profile
from pstats import Stats
from pathlib import Path

from wdom.parser import parse_html
from wdom.server import _tornado

# fake connection
_tornado.connections.append(1)  # type: ignore

root = Path(__file__).absolute().parent.parent
html_file = root / 'docs/_build/html/node.html'
with open(html_file) as f:
    real_html = f.read()

src = '<div>' + '''
  <div a="1">
    <span b="2">text</span>
    <span b="2">text</span>
    <span b="2">text</span>
    <span b="2">text</span>
  </div>
''' * 1000 + '</div>'

if __name__ == '__main__':
    profiler = Profile()
    # profiler.runcall(parse_html, real_html)
    profiler.runcall(parse_html, src)  # ~1.7 sec
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats()
