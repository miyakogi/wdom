#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Event/Message handlers for web server."""

import json
import logging
from typing import Dict

from wdom.event import Event, create_event, EventMsgDict

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


def create_event_from_msg(msg: EventMsgDict) -> Event:
    """Create Event from dictionally (JSON message).

    Message format:
        {
            'proto': 'event.__proto__.toString()',
            'type': 'event type',
            'currentTarget': {
                'id': 'wdom_id of target node',
                ... (additional information),
                },
            'target': {
                'id': 'wdom_id of target node',
                ... (additional information),
                },
            ...,  // event specific fields
            }
    """
    return create_event(msg)


def event_handler(msg: EventMsgDict) -> Event:
    """Handle events emitted on browser."""
    e = create_event_from_msg(msg)
    if e.currentTarget is None:
        if e.type not in ['mount', 'unmount']:
            id = msg['currentTarget']['id']
            logger.warning('No such element: wdom_id={}'.format(id))
        return e
    e.currentTarget.on_event_pre(e)
    e.currentTarget.dispatchEvent(e)
    return e


def response_handler(msg: Dict[str, str]) -> None:
    """Handle response sent by browser."""
    from wdom.document import getElementByWdomId
    id = msg['id']
    elm = getElementByWdomId(id)
    if elm:
        elm.on_response(msg)
    else:
        logger.warning('No such element: wdom_id={}'.format(id))


def on_websocket_message(message: str) -> None:
    """Handle messages from browser."""
    msgs = json.loads(message)
    for msg in msgs:
        if not isinstance(msg, dict):
            logger.error('Invalid WS message format: {}'.format(message))
            continue
        _type = msg.get('type')
        if _type == 'log':
            log_handler(msg['level'], msg['message'])
        elif _type == 'event':
            event_handler(msg['event'])
        elif _type == 'response':
            response_handler(msg)
        else:
            raise ValueError('Unkown message type: {}'.format(message))
