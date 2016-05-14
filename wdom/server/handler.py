#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging

from wdom.interface import Event

logger = logging.getLogger(__name__)


def log_handler(level: str, message: str):
    """Handle logs from client (browser)."""
    message = 'JS: ' + str(message)
    if level == 'error':
        logger.error(message)
    elif level == 'warn':
        logger.warning(message)
    elif level == 'info':
        logger.info(message)
    elif level == 'debug':
        logger.debug(message)


def event_handler(msg: dict):
    """Handle events emitted on browser."""
    from wdom.document import getElementByRimoId
    e = Event(**msg.get('event'))
    _id = e.currentTarget.get('id')
    currentTarget = getElementByRimoId(_id)
    if currentTarget is None:
        logger.warning('No such element: rimo_id={}'.format(_id))
        return

    currentTarget.on_event_pre(e)
    e.currentTarget = currentTarget
    e.target = getElementByRimoId(e.target.get('id'))
    e.currentTarget.dispatchEvent(e)


def response_handler(msg: dict):
    """Handle response sent by browser."""
    from wdom.document import getElementByRimoId
    id = msg.get('id')
    elm = getElementByRimoId(id)
    if elm:
        elm.on_response(msg)
    else:
        logger.warning('No such element: rimo_id={}'.format(id))


def on_websocket_message(message):
    """Handle messages from browser."""
    msg = json.loads(message)
    _type = msg.get('type')
    if _type == 'log':
        log_handler(msg.get('level'), msg.get('message'))
    elif _type == 'event':
        event_handler(msg)
    elif _type == 'response':
        response_handler(msg)
    else:
        raise ValueError('unkown message type: {}'.format(message))
