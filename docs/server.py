#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

from livereload import Server, shell

subprocess.run(['make', 'html'])

server = Server()
# Wtach documets
server.watch('*.rst', shell('make html'))
server.watch('./*/*.rst', shell('make html'))
server.watch('./*/*/*.rst', shell('make html'))

# Watch template/style
server.watch('_templates/*.html', shell('make html'))
server.watch('_static/*.css', shell('make html'))
server.watch('_static/*.js', shell('make html'))

# Watch package
server.watch('../*/*.py', shell('make html'))
server.watch('../*/*/*.py', shell('make html'))
server.watch('../*/*/*/*.py', shell('make html'))

server.serve(port=8889, root='_build/html')
