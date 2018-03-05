#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

from setuptools import setup

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.rst')
with open(readme_file) as f:
    readme = f.read()

install_requires = [
    'tornado>=5.0',
]
test_requires = [
    'parameterized',
    'selenium',
    'syncer',
    'pyppeteer',
]


setup(
    name='wdom',
    version='0.3.1',
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
    ],
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='dom browser gui ui',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: User Interfaces',
    ],
    python_requires='>=3.5.2',
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='tests',
)
