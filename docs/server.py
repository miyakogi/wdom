#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

from livereload import Server, shell

subprocess.run(['make', 'clean'])
subprocess.run(['make', 'html'])

server = Server()
make = shell(['make', 'html'])
clean_make = shell(['make', 'clean', '&&', 'make', 'html'])

# Wtach documets
server.watch('../*.rst', make)
server.watch('*.rst', make)
server.watch('./*/*.rst', make)
server.watch('./*/*/*.rst', make)

# Watch template/style
server.watch('./_templates/*.html', make)
server.watch('./_static/*.css', clean_make)
server.watch('./_static/*.js', make)

# Watch package
server.watch('../*/*.py', make)
server.watch('../*/*/*.py', make)
server.watch('../*/*/*/*.py', make)

server.serve(port=8889, root='_build/html', debug=True)
