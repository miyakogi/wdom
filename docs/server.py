#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import subprocess

from livereload import Server
from livereload import watcher

watcher.pyinotify = None  # disable pyinotiry

docsdir = path.dirname(path.abspath(__file__))
builddir = path.join(docsdir, '_build')
build_cmd = [
    'sphinx-build', '-b', 'html', '-j', '4',
    '-d', path.join(builddir, 'doctrees'),
    docsdir, path.join(builddir, 'html'),
]


def cmd() -> None:
    subprocess.run(build_cmd, cwd=docsdir)


def docs(p: str) -> str:
    return path.join(docsdir, p)


# subprocess.run(['make', 'clean'], cwd=docsdir)
cmd()  # build once
server = Server()

# Wtach documets
server.watch(docs('*.md'), cmd, delay=1)
server.watch(docs('*.rst'), cmd, delay=1)
server.watch(docs('../*.rst'), cmd, delay=1)
server.watch(docs('*/*.rst'), cmd, delay=1)
server.watch(docs('*/*.md'), cmd, delay=1)
server.watch(docs('*/*/*.rst'), cmd, delay=1)
server.watch(docs('*/*/*.md'), cmd, delay=1)

# Watch template/style
server.watch(docs('_templates/'), cmd, delay=1)
server.watch(docs('_static/'), cmd, delay=1)

# Watch package
server.watch(docs('../wdom/*.py'), cmd, delay=1)
server.watch(docs('../wdom/*/*.py'), cmd, delay=1)
server.watch(docs('../wdom/*/*/*.py'), cmd, delay=1)
server.watch(docs('../wdom/*/*/*/*.py'), cmd, delay=1)

server.serve(port=8889, root=docs('_build/html'), debug=True, restart_delay=1)
