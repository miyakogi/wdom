#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from livereload import Server, shell

server = Server()
server.watch('*.rst', shell('make html'))
server.watch('./*/*.rst', shell('make html'))
server.watch('./*/*/*.rst', shell('make html'))
server.watch('../*/*.py', shell('make html'))
server.watch('../*/*/*.py', shell('make html'))
server.watch('../*/*/*/*.py', shell('make html'))
server.serve(port=8889, root='_build/html')
