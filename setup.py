#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.rst')
with open(readme_file) as readme_file:
    readme = readme_file.read()

install_requires = ['tornado']
test_requites = ['pytest', 'pytest-cov', 'aiohttp', 'syncer']

setup(
    name='wdom',
    version='0.0.1',
    description='A library to manipulate DOM on browsers',
    long_description=readme,
    author='Hiroyuki Takagi',
    author_email='miyako.dev@gmail.com',
    url='https://github.com/miyakogi/wdom_py',
    py_modules=['wdom'],
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
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',

    install_requires=install_requires,
)
