#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import subprocess

from livereload import Server, shell

docsdir = path.dirname(path.abspath(__file__))
builddir = path.join(docsdir, '_build')

subprocess.run(['make', 'clean'])
subprocess.run(['make', 'html'])

server = Server()
cmd = shell(['sphinx-build', '-b', 'html', '-E',
             '-d', path.join(builddir, 'doctrees'),
             docsdir, path.join(builddir, 'html')])

# Wtach documets
server.watch('../*.rst', cmd, delay=1)
server.watch('*.rst', cmd, delay=1)
server.watch('./*/*.rst', cmd, delay=1)
server.watch('./*/*/*.rst', cmd, delay=1)

# Watch template/style
server.watch('./_templates/*.html', cmd, delay=1)
server.watch('./_static/*.css', cmd, delay=1)
server.watch('./_static/*.js', cmd, delay=1)

# Watch theme
server.watch('./themes/slex/static/*.css_t', cmd, delay=1)
server.watch('./themes/slex/*.html', cmd, delay=1)
server.watch('./themes/slex/theme.conf', cmd, delay=1)

# Watch package
server.watch('../*/*.py', cmd, delay=1)
server.watch('../*/*/*.py', cmd, delay=1)
server.watch('../*/*/*/*.py', cmd, delay=1)

server.serve(port=8889, root='_build/html', debug=True, restart_delay=1)
