/* wdom.js v0.1.0 alpha, @lisence MIT, copyright 2016, miyakogi */

;(function(window, undefined){
  'use strict';
  // Define global object
  const wdom = { version: '0.1.0', settings: {}, log: { level: 0 }}
  const config_prefix = 'WDOM_'

  const log_levels = {
    FATAL: 50,
    CRITICAL: 50,
    ERROR: 40,
    WARNING: 30,
    WARN: 30,
    INFO: 20,
    DEBUG: 10,
    NOTSET: 0,
  }

  const element_with_value = ['INPUT', 'TEXTAREA', 'SELECT']
  const event_data_map = {
    'input': ['value'],
    'change': ['checked', 'value']
  }

  function get_log_level(level) {
    if (typeof level === 'number'){
      return level
    }

    if (typeof level === 'string') {
      const s = level.toUpperCase()
      if (s in log_levels) {
        return log_levels[s]
      }
    }

    // Get unknown log level
    console.warn(wdom.settings.LOG_PREFIX + `unknown log level: ${level}`)
    return 0
  }

  function set_default(key, defval) {
    if (config_prefix + key in window) {
      wdom.settings[key] = window[config_prefix + key]
    } else {
      wdom.settings[key] = defval
    }
  }

  function get_node(id) {
    if (id === 'window') {
      return window
    } else if (id === 'document') {
      return document
    } else {
      return document.querySelector(`[wdom_id="${id}"]`)
    }
  }

  function get_wdom_id(node) {
    if (node === window) {
      return 'window'
    } else if (node === document) {
      return 'document'
    } else {
      return node.getAttribute('wdom_id')
    }
  }

  function is_wdom_node(node) {
    return  node === document || node === window || node.hasAttribute('wdom_id')
  }

  function node_mounted(node) {
    if (!is_wdom_node(node)) { return }
    wdom.send_event({type: 'mount', target: node, currentTarget: node})
    if (element_with_value.indexOf(node.tagName) >= 0) {
      node.addEventListener('input', wdom.send_event, false)
      node.addEventListener('change', wdom.send_event, false)
    }
  }

  function node_unmounted(node) {
    if (!is_wdom_node(node)) { return }
    wdom.send_event({type: 'unmount', target: node, currentTarget: node})
  }

  function mutation_handler(m) {
    let i, node
    for (i=0; i < m.addedNodes.length; i++) {
      node = m.addedNodes[i]
      if (node && node.nodeType === Node.ELEMENT_NODE && node.hasAttribute('wdom_id')) {
        node_mounted(node)
      }
    }
    for (i=0; i < m.removedNodes.length; i++) {
      node = m.addedNodes[i]
      if (node && node.nodeType === Node.ELEMENT_NODE && node.hasAttribute('wdom_id')) {
        node_unmounted(node)
      }
    }
  }

  function start_observer() {
    // initialize observer
    const observer = new MutationObserver(
      function(mutations) {
        mutations.forEach(mutation_handler)
      }
    )
    const obs_conf = {
      'childList': true,
      'subtree': true,
    }
    observer.observe(document, obs_conf)
  }

  function ws_onopen() {
    // Start msg sending loop
    wdom.msg_loop()
    // Send pending events
    wdom.pending_msgs.forEach(function(msg) {
      wdom.push_msg(msg)
    })
    wdom.pending_msgs = []
  }

  function ws_onmessage(e) {
    const data = e.data
    setTimeout(function() {
      const msgs = JSON.parse(data)
      msgs.forEach(msg_to_node)
    }, 0)
  }

  function msg_to_node(msg) {
    const target = msg.target
    if (target === 'node') {
      let node = get_node(msg.id)
      if (!node) {
        // node may not have been mounted yet. retry 100ms later.
        setTimeout(function() {
          let node = get_node(msg.id)
            if (!node) {
              // node not found. send warning.
              wdom.log.console('warn', `gat message to unknown node (id=${msg.id}).\n Message: ${msg}`)
              wdom.log.warn(`unknown node: id=${msg.id}, method=${msg.method}`)
            } else {
              wdom.exec(node, msg.method, msg.params)
            }
        }, 100)
      } else {
        wdom.exec(node, msg.method, msg.params)
      }
    }
  }

  function ws_onclose() {
    function reload() {
      let _retry = 0
      const xmlhttp = new XMLHttpRequest()

      const open = function() {
        console.log('Reloading...' + Array(_retry).join('.'))
        xmlhttp.open('GET', 'http://' + location.host)
        xmlhttp.send()
      }

      const check_reload = function() {
        if (xmlhttp.readyState == 4) {
          if (xmlhttp.status == 200) {
            location.reload()
          } else {
            _retry += 1
            if (_retry < 100) {
              setTimeout(open, wdom.settings.RELOAD_WAIT)
            } else {
              wdom.log.console('error', 'Server auto-reload failed.')
            }
          }
        }
      }

      xmlhttp.onreadystatechange = check_reload
      open()
    }

    if (wdom.settings.AUTORELOAD) {
      wdom.log.console('info', 'RootWS closed, reloading page...')
      setTimeout(reload, wdom.settings.RELOAD_WAIT)
    } else {
      wdom.log.console('RootWS CLOSED');
    }
  }

  function initialize() {
    // Define default variables
    const __ws_url = 'ws://' + location.host + '/wdom_ws'
    set_default('DEBUG', false)
    set_default('AUTORELOAD', false)
    set_default('RELOAD_WAIT', 100)
    set_default('MESSAGE_WAIT', 0.005)
    set_default('LOG_LEVEL', 'WARN')
    set_default('LOG_PREFIX', 'wdom: ')
    set_default('LOG_CONSOLE', false)
    set_default('WS_URL', __ws_url)
    wdom.log.set_level(wdom.settings.LOG_LEVEL)

    // Make root WebScoket connection
    wdom.ws = new WebSocket(wdom.settings.WS_URL)
    wdom.ws.addEventListener('open', ws_onopen, false)
    wdom.ws.addEventListener('message', ws_onmessage, false)
    wdom.ws.addEventListener('close', ws_onclose, false)

    node_mounted(document)
    node_mounted(window)
  }

  wdom.exec = function(node, method, params) {
    // Execute fucntion with msg
    setTimeout(function() {
      const args = [node].concat(params)
      wdom[method].apply(wdom, args)
    }, 0)
  }

  wdom.eval = function(node, script) {
    // Execute fucntion with msg
    setTimeout(function() {
      try {
        eval(script)
      }
      catch (e) {
        wdom.log.error(e.toString())
        wdom.log.console('error', e.toString())
      }
    }.bind(node), 0)
  }

  wdom.pending_msgs = []
  wdom.msg_queue = []

  wdom.push_msg = function(msg) {
    wdom.msg_queue.push(msg)
  }

  wdom.msg_loop = function() {
    setTimeout(function() {
      if (wdom.msg_queue.length > 0) {
        const msg = JSON.stringify(wdom.msg_queue)
        wdom.msg_queue.length = 0
        wdom.send(msg)
      }
      wdom.msg_loop()
    }, wdom.settings.MESSAGE_WAIT)
  }

  wdom.send = function(msg, retry) {
    if ('ws' in wdom) {
      if (wdom.ws.readyState ===  1) { 
        wdom.ws.send(msg)
      } else {
        retry = retry ? retry + 1 : 1
        if (retry < 5) {
          setTimeout(function() { wdom.send(msg, retry) }, 200)
        } else {
          setTimeout(function() { wdom.send(msg) }, 200)
        }
      }
    } else {
      wdom.pending_msgs.push(msg)
    }
  }

  // send response
  wdom.send_response = function(node, reqid, data) {
    const msg = {
      type: 'response',
      id: get_wdom_id(node),
      reqid: reqid,
      data: data
    }
    wdom.push_msg(msg)
  }

  /* Event control */
  // send events emitted on the browser to the server
  const EventMap = {
    'UIEvent': [],
    'MouseEvent': ['altKey', 'button', 'clientX', 'clientY', 'ctrlKey',
      'metaKey', 'movementX', 'movementY', 'offsetX', 'offsetY', 'pageX',
      'pageY', 'region', 'screenX', 'screenY', 'shiftKey', 'x', 'y'],
    'InputEvent': ['data'],
    'KeyboardEvent': ['altKey', 'code', 'ctrlKey', 'key', 'locale', 'metaKey',
      'repeat', 'shiftKey'],
  }
  let _data_transfer_id = 1
  wdom.send_event = function(e) {
    // Catch currentTarget here. In callback, it becomes different node or null,
    // since event bubbles up.
    const currentTarget = e.currentTarget
    const target = e.target
    if (!is_wdom_node(currentTarget)) { return }

    // define func here to capture e and event
    function copy_event_attrs(event_class) {
      EventMap[event_class].forEach(function(attr) {
        event[attr] = e[attr]
      })
    }

    /* Event Object Format
      event = {
        proto: event.__proto__.toString(),
        type: event.type,
        currentTarget: {
          id: wdom_id of the currentTarget,
          ...,  // some info of the currentTarget, like value/checked
        },
        target: {
          id: wdom_id of the currentTarget,
          ...,  // some info of the target
        },
        dataTransfer: {
          id: data transfer id for wdom,
          ..., // data if exists
        },
        ..., // event specific fields
      }
    */
    const proto = e.toString().replace(/\[object (.+)\]/, '\$1')
    const event = {
      'proto': proto,
      'type': e.type,
      'currentTarget': {'id': get_wdom_id(currentTarget)},
      'target': {'id': get_wdom_id(e.target)}
    }

    // Mouse Event
    if (e instanceof MouseEvent) {
      if (e.relatedTarget !== null) {
        event.relatedTarget = {id: get_wdom_id(e.relatedTarget)}
      } else {
        event.relatedTarget = null
      }
      copy_event_attrs('MouseEvent') // Copy event attributes
    }

    // Drag Event
    if (e instanceof DragEvent) {
      if (e.type === 'drop') {
        e.preventDefault()  // Necessary to enable drop.
      }

      // Add DataTransfer id
      // dragstart: read/write enabled
      // drop: read enabled
      // others: disabled
      event.dataTransfer = {}
      const dt = e.dataTransfer
      if (e.type === 'dragstart') {
        const _id = _data_transfer_id.toString()
        dt.setData('wdom/id', _id)
        currentTarget.__dt_id = _id
        currentTarget.__dragged = true
        _data_transfer_id += 1
      }
      event.dataTransfer.id = dt.getData('wdom/id') || currentTarget.__dt_id || ''
      if (e.type === 'dragend' && currentTarget.__dragged) {
        delete currentTarget.__dragged
        delete currentTarget.__dt_id
      }
    }

    // Add event specific attributes
    if (proto in EventMap) {
      for (let i in EventMap[proto]) {
        const attr = EventMap[proto][i]
        event[attr] = e[attr]
      }
    }

    // On input/change events, copy data to the server node
    if (e.type in event_data_map) {
      event_data_map[e.type].forEach(function(prop) {
        event.target[prop] = e.target[prop]
        event.currentTarget[prop] = currentTarget[prop]
      })
    }
    if (currentTarget.localName === 'select') {
      const selected = []
      const len = currentTarget.selectedOptions.length
      for (let i=0; i < len; i++) {
        let opt = currentTarget.selectedOptions[i]
        selected.push(get_wdom_id(opt))
      }
      event.currentTarget.selectedOptions = selected
    }

    /* Event message format
        msg = {
          type: 'event',
          event: event object,
          id: wdom_id of the currentTarget,
        }
    */
    const msg = {
      type: 'event',
      event: event,
      id: get_wdom_id(currentTarget)
    }
    wdom.push_msg(msg)
  }

  // Add event listener
  wdom.addEventListener = function(node, event) {
    node.addEventListener(event, wdom.send_event, false)
    if (event === 'dragstart') {
      // Send drag-end signal to remove data on dataTransfer on server
      node.addEventListener('dragend', wdom.send_event, false)
    } else if (event === 'drop') {
      node.addEventListener('dragover', function(e) {
        e.preventDefault()  // Necessary to enable drop.
      })
    }
  }

  wdom.removeEventListener = function(node, event) {
    node.removeEventListener(event, wdom.send_event)
  }

  /* DOM control */
  wdom.insert = function(node, ind, html) {
    const index = Number(ind)
    if (!node.hasChildNodes() || index >= node.childNodes.length) {
      node.insertAdjacentHTML('beforeend', html)
    } else {
      const ref_node = node.childNodes[index]
      if (ref_node.nodeType !== 1) {
        // There may be better way...
        const _ = document.createElement('template')
        _.innerHTML = html
        // no need to clone contents, since this template is used once
        ref_node.parentNode.insertBefore(_.content, ref_node)
      } else {
        ref_node.insertAdjacentHTML('beforebegin', html)
      }
    }
  }

  wdom.insertAdjacentHTML = function(node, position, html) {
    node.insertAdjacentHTML(position, html)
  }

  wdom.textContent = function(node, text) {
    node.textContent = text
  }

  wdom.innerHTML = function(node, html) {
    node.innerHTML = html
  }

  wdom.outerHTML = function(node, html) {
    node.outerHTML = html
  }

  wdom.removeChildById = function(node, id) {
    const child = get_node(id)
    if (child) { node.removeChild(child) }
  }

  wdom.removeChildByIndex = function(node, index) {
    const child = node.childNodes.item(index)
    if (child) { node.removeChild(child) }
  }

  wdom.replaceChildById = function(node, html, id) {
    const old_child = get_node(id)
    if (old_child) {
      old_child.insertAdjacentHTML('beforebegin', html)
      old_child.parentNode.removeChild(old_child)
    }
  }

  wdom.replaceChildByIndex = function(node, html, index) {
    const old_child = node.childNodes.item(index)
    if (old_child) {
      wdom.insert(node, index, html)
      old_child.parentNode.removeChild(old_child)
    }
  }

  wdom.removeAttribute = function(node, attr) {
    node.removeAttribute(attr)
  }

  wdom.setAttribute = function(node, attr, value) {
    if (attr in node) {
      // some boolean values, like hidden, fail on setAttribute
      node[attr] = value
    } else {
      node.setAttribute(attr, value)
    }
  }

  wdom.addClass = function(node, classes) {
    // I won't support IE and Safari...
    // node.classList.add(...params.classes)
    node.classList.add.apply(node.classList, classes)
  }

  wdom.removeClass = function(node, classes) {
    // I won't support IE and Safari...
    // node.classList.remove(...params.classes)
    node.classList.remove.apply(node.classList, classes)
    if (node.classList.length == 0 && node.hasAttribute('class')) {
      node.removeAttribute('class')
    }
  }

  wdom.empty = function(node) {
    node.innerHTML = ''
  }

  wdom.getBoundingClientRect = function(node, reqid) {
    const rect = node.getBoundingClientRect()
    wdom.send_response(node, reqid, {
      bottom: rect.bottom,
      height: rect.height,
      left: rect.left,
      right: rect.right,
      top: rect.top,
      width: rect.width
    })
  }

  /* Event Control */
  wdom.click = function(node) {
    node.click()
  }

  /* Window Control */
  wdom.scroll = function(node, x, y){
    window.scrollTo(x, y)
  }

  wdom.scrollTo = function(node, x, y){
    window.scrollTo(x, y)
  }

  wdom.scrollBy = function(node, x, y){
    window.scrollBy(x, y)
  }

  wdom.scrollX = function(node, reqid){
    wdom.send_response(node, reqid, {x: window.scrollX})
  }

  wdom.scrollY = function(node, reqid){
    wdom.send_response(node, reqid, {y: window.scrollY})
  }

  wdom.log.log = function(level, message) {
    const msg = {
      type: 'log',
      level: level,
      message: message
    }

    if (wdom.settings.LOG_CONSOLE) {
      wdom.log.console(level, message)
    }
    wdom.push_msg(msg)
  }

  wdom.log.console = function(level, message) {
    if (wdom.log.level <= get_log_level(level) && 'console' in window) {
      console[level](wdom.settings.LOG_PREFIX + message)
    }
  }

  wdom.log.set_level = function(level) {
    wdom.log.level = get_log_level(level)
  }

  wdom.log.error = function(message) {
    wdom.log.log('error', message)
  }

  wdom.log.warn = function(message) {
    wdom.log.log('warn', message)
  }

  wdom.log.info = function(message) {
    wdom.log.log('info', message)
  }

  wdom.log.debug = function(message) {
    wdom.log.log('debug', message)
  }

  // Register object to global
  window.addEventListener('load', initialize, false)
  start_observer()
})(typeof window != 'undefined' ? window : void 0);
