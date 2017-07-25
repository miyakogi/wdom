#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from typing import Dict, Any

from wdom.interface import Event

logger = logging.getLogger(__name__)


def log_handler(level: str, message: str) -> None:
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


def event_handler(msg: Dict[str, Any]) -> None:
    """Handle events emitted on browser."""
    from wdom.document import getElementByRimoId
    event_msg = msg['event']  # type: Dict[str, str]
    e = Event(**event_msg)
    _id = e.currentTarget.get('id')
    currentTarget = getElementByRimoId(_id)
    if currentTarget is None:
        if e.type not in ['mount', 'unmount']:
            logger.warning('No such element: rimo_id={}'.format(_id))
        return

    currentTarget.on_event_pre(e)
    e.currentTarget = currentTarget
    e.target = getElementByRimoId(e.target.get('id'))
    e.currentTarget.dispatchEvent(e)


def response_handler(msg: Dict[str, str]) -> None:
    """Handle response sent by browser."""
    from wdom.document import getElementByRimoId
    id = msg['id']
    elm = getElementByRimoId(id)
    if elm:
        elm.on_response(msg)
    else:
        logger.warning('No such element: rimo_id={}'.format(id))


def on_websocket_message(message: str) -> None:
    """Handle messages from browser."""
    msgs = json.loads(message)
    for msg in msgs:
        _type = msg.get('type')
        if _type == 'log':
            log_handler(msg.get('level'), msg.get('message'))
        elif _type == 'event':
            event_handler(msg)
        elif _type == 'response':
            response_handler(msg)
        else:
            raise ValueError('unkown message type: {}'.format(message))
