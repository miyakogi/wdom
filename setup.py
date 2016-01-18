#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cx_Freeze import setup, Executable
from wdom.misc import include_dirs

__version__ = '0.0.1'
__author__ = 'miyakogi'

build_exe_options = {
    'include_files': include_dirs,
}


def main() -> None:
    setup(
        name = 'click',
        version = __version__,
        description = 'sample',
        executables = [Executable('sample.py')],
        options = {'build_exe': build_exe_options}
    )


if __name__ == '__main__':
    main()
