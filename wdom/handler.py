#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from wdom.interface import Event
from wdom.document import Document

logger = logging.getLogger(__name__)


def log_handler(level: str, message: str):
    message = 'JS: ' + str(message)
    if level == 'error':
        logger.error(message)
    elif level == 'warn':
        logger.warn(message)
    elif level == 'info':
        logger.info(message)
    elif level == 'debug':
        logger.debug(message)


def event_handler(msg: dict, doc: Document):
    e = Event(**msg.get('event'))
    _id = e.currentTarget.get('id')
    currentTarget = doc.getElementByRimoId(_id)
    if currentTarget is None:
        logger.warn('No such element: rimo_id={}'.format(_id))
        return

    if e.type in ('input', 'change'):
        # Update user inputs
        if currentTarget.tagName == 'INPUT':
            if currentTarget.type.lower() in ('checkbox', 'radio'):
                currentTarget._set_attribute(
                    'checked', e.currentTarget.get('checked'))
            else:
                currentTarget._set_attribute(
                    'value', e.currentTarget.get('value'))
        elif currentTarget.tagName == 'TEXTAREA':
            currentTarget._set_text_content(e.currentTarget.get('value'))
        elif currentTarget.tagName == 'SELECT':
            currentTarget._set_attribute('value', e.currentTarget.get('value'))
    e.currentTarget = currentTarget
    e.target = doc.getElementByRimoId(e.target.get('id'))
    e.currentTarget.dispatchEvent(e)


def response_handler(msg: dict, doc:Document):
    id = msg.get('id')
    elm = doc.getElementByRimoId(id)
    if elm is not None:
        elm.on_message(msg)
    else:
        logger.warn('No such element: rimo_id={}'.format(id))
