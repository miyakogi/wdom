#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import webbrowser


def open_browser(url, browser):
    if browser in webbrowser._browsers:
        webbrowser.get(browser).open(url)
    else:
        webbrowser.open(url)
