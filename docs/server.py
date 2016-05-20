#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

from livereload import Server, shell

subprocess.run(['make', 'clean'])
subprocess.run(['make', 'html'])

server = Server()
make = shell(['make', 'html'])
# clean_make = shell(['make', 'html_all'])

# Wtach documets
server.watch('../*.rst', make)
server.watch('*.rst', make)
server.watch('./*/*.rst', make)
server.watch('./*/*/*.rst', make)

# Watch template/style
server.watch('./_templates/*.html', make)
server.watch('./_static/*.css', make)
server.watch('./_static/*.js', make)

# Watch theme
server.watch('./alabaster/alabaster/static/*.css_t', make)
server.watch('./alabaster/alabaster/*.html', make)
server.watch('./alabaster/alabaster/theme.conf', make)

# Watch package
server.watch('../*/*.py', make)
server.watch('../*/*/*.py', make)
server.watch('../*/*/*/*.py', make)

server.serve(port=8889, root='_build/html', debug=True)
