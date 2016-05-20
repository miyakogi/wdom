#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.rst')
with open(readme_file) as readme_file:
    readme = readme_file.read()

install_requires = ['tornado']
test_requites = ['nose_parameterized', 'selenium', 'syncer']

if sys.version_info < (3, 5):
    install_requires.append('mypy-lang')


setup(
    name='wdom',
    version='0.1.4',
    description='GUI library for browser-based desktop applications',
    long_description=readme,
    author='Hiroyuki Takagi',
    author_email='miyako.dev@gmail.com',
    url='https://github.com/miyakogi/wdom',
    packages=[
        'wdom',
        'wdom.examples',
        'wdom.server',
        'wdom.themes',
        'wdom.tests',
        'wdom.tests.local_browser',
        'wdom.tests.remote_browser',
    ],
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='dom browser',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='wdom.tests',

    install_requires=install_requires,
)
