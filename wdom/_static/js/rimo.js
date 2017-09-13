/* rimo v0.0.1 alpha, @lisence MIT, copyright 2016, miyakogi */

;(function(window, undefined){
  'use strict';
  // Define global object
  const rimo = { version: '0.0.1', settings: {}, log: { level: 0 }}
  const config_prefix = 'RIMO_'

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
    console.warn(rimo.settings.LOG_PREFIX + `unknown log level: ${level}`)
    return 0
  }

  function set_default(key, defval) {
    if (config_prefix + key in window) {
      rimo.settings[key] = window[config_prefix + key]
    } else {
      rimo.settings[key] = defval
    }
  }

  function get_node(id) {
    if (id === 'window') {
      return window
    } else if (id === 'document') {
      return document
    } else {
      return document.querySelector(`[rimo_id="${id}"]`)
    }
  }

  function get_rimo_id(node) {
    if (node === window) {
      return 'window'
    } else if (node === document) {
      return 'document'
    } else {
      return node.getAttribute('rimo_id')
    }
  }

  function is_rimo_node(node) {
    return  node === document || node === window || node.hasAttribute('rimo_id')
  }

  function node_mounted(node) {
    if (!is_rimo_node(node)) { return }
    rimo.send_event({type: 'mount', target: node, currentTarget: node})
    if (element_with_value.indexOf(node.tagName) >= 0) {
      node.addEventListener('input', rimo.send_event, false)
      node.addEventListener('change', rimo.send_event, false)
    }
  }

  function node_unmounted(node) {
    if (!is_rimo_node(node)) { return }
    rimo.send_event({type: 'unmount', target: node, currentTarget: node})
  }

  function mutation_handler(m) {
    let i, node
    for (i=0; i < m.addedNodes.length; i++) {
      node = m.addedNodes[i]
      if (node && node.nodeType === Node.ELEMENT_NODE && node.hasAttribute('rimo_id')) {
        node_mounted(node)
      }
    }
    for (i=0; i < m.removedNodes.length; i++) {
      node = m.addedNodes[i]
      if (node && node.nodeType === Node.ELEMENT_NODE && node.hasAttribute('rimo_id')) {
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
    rimo.msg_loop()
    // Send pending events
    rimo.pending_msgs.forEach(function(msg) {
      rimo.push_msg(msg)
    })
    rimo.pending_msgs = []
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
              rimo.log.console('warn', `gat message to unknown node (id=${msg.id}).\n Message: ${msg}`)
              rimo.log.warn(`unknown node: id=${msg.id}, method=${msg.method}`)
            } else {
              rimo.exec(node, msg.method, msg.params)
            }
        }, 100)
      } else {
        rimo.exec(node, msg.method, msg.params)
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
              setTimeout(open, rimo.settings.RELOAD_WAIT)
            } else {
              rimo.log.console('error', 'Server auto-reload failed.')
            }
          }
        }
      }

      xmlhttp.onreadystatechange = check_reload
      open()
    }

    if (rimo.settings.AUTORELOAD) {
      rimo.log.console('info', 'RootWS closed, reloading page...')
      setTimeout(reload, rimo.settings.RELOAD_WAIT)
    } else {
      rimo.log.console('RootWS CLOSED');
    }
  }

  function initialize() {
    // Define default variables
    const __ws_url = 'ws://' + location.host + '/rimo_ws'
    set_default('DEBUG', false)
    set_default('AUTORELOAD', false)
    set_default('RELOAD_WAIT', 100)
    set_default('MESSAGE_WAIT', 0.005)
    set_default('LOG_LEVEL', 'WARN')
    set_default('LOG_PREFIX', 'rimo: ')
    set_default('LOG_CONSOLE', false)
    set_default('WS_URL', __ws_url)
    rimo.log.set_level(rimo.settings.LOG_LEVEL)

    // Make root WebScoket connection
    rimo.ws = new WebSocket(rimo.settings.WS_URL)
    rimo.ws.addEventListener('open', ws_onopen, false)
    rimo.ws.addEventListener('message', ws_onmessage, false)
    rimo.ws.addEventListener('close', ws_onclose, false)

    node_mounted(document)
    node_mounted(window)
  }

  rimo.exec = function(node, method, params) {
    // Execute fucntion with msg
    setTimeout(function() {
      const args = [node].concat(params)
      rimo[method].apply(rimo, args)
    }, 0)
  }

  rimo.eval = function(node, script) {
    // Execute fucntion with msg
    setTimeout(function() {
      try {
        eval(script)
      }
      catch (e) {
        rimo.log.error(e.toString())
        rimo.log.console('error', e.toString())
      }
    }.bind(node), 0)
  }

  rimo.pending_msgs = []
  rimo.msg_queue = []

  rimo.push_msg = function(msg) {
    rimo.msg_queue.push(msg)
  }

  rimo.msg_loop = function() {
    setTimeout(function() {
      if (rimo.msg_queue.length > 0) {
        const msg = JSON.stringify(rimo.msg_queue)
        rimo.msg_queue.length = 0
        rimo.send(msg)
      }
      rimo.msg_loop()
    }, rimo.settings.MESSAGE_WAIT)
  }

  rimo.send = function(msg, retry) {
    if ('ws' in rimo) {
      if (rimo.ws.readyState ===  1) { 
        rimo.ws.send(msg)
      } else {
        retry = retry ? retry + 1 : 1
        if (retry < 5) {
          setTimeout(function() { rimo.send(msg, retry) }, 200)
        } else {
          setTimeout(function() { rimo.send(msg) }, 200)
        }
      }
    } else {
      rimo.pending_msgs.push(msg)
    }
  }

  // send response
  rimo.send_response = function(node, reqid, data) {
    const msg = {
      type: 'response',
      id: get_rimo_id(node),
      reqid: reqid,
      data: data
    }
    rimo.push_msg(msg)
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
  rimo.send_event = function(e) {
    // Catch currentTarget here. In callback, it becomes different node or null,
    // since event bubbles up.
    const currentTarget = e.currentTarget
    const target = e.target
    if (!is_rimo_node(currentTarget)) { return }

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
          id: rimo_id of the currentTarget,
          ...,  // some info of the currentTarget, like value/checked
        },
        target: {
          id: rimo_id of the currentTarget,
          ...,  // some info of the target
        },
        dataTransfer: {
          id: data transfer id for rimo,
          ..., // data if exists
        },
        ..., // event specific fields
      }
    */
    const proto = e.toString().replace(/\[object (.+)\]/, '\$1')
    const event = {
      'proto': proto,
      'type': e.type,
      'currentTarget': {'id': get_rimo_id(currentTarget)},
      'target': {'id': get_rimo_id(e.target)}
    }

    // Mouse Event
    if (e instanceof MouseEvent) {
      if (e.relatedTarget !== null) {
        event.relatedTarget = {id: get_rimo_id(e.relatedTarget)}
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
        dt.setData('rimo/id', _id)
        currentTarget.__dt_id = _id
        currentTarget.__dragged = true
        _data_transfer_id += 1
      }
      event.dataTransfer.id = dt.getData('rimo/id') || currentTarget.__dt_id || ''
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
        selected.push(get_rimo_id(opt))
      }
      event.currentTarget.selectedOptions = selected
    }

    /* Event message format
        msg = {
          type: 'event',
          event: event object,
          id: rimo_id of the currentTarget,
        }
    */
    const msg = {
      type: 'event',
      event: event,
      id: get_rimo_id(currentTarget)
    }
    rimo.push_msg(msg)
  }

  // Add event listener
  rimo.addEventListener = function(node, event) {
    node.addEventListener(event, rimo.send_event, false)
    if (event === 'dragstart') {
      // Send drag-end signal to remove data on dataTransfer on server
      node.addEventListener('dragend', rimo.send_event, false)
    } else if (event === 'drop') {
      node.addEventListener('dragover', function(e) {
        e.preventDefault()  // Necessary to enable drop.
      })
    }
  }

  rimo.removeEventListener = function(node, event) {
    node.removeEventListener(event, rimo.send_event)
  }

  /* DOM control */
  rimo.insert = function(node, ind, html) {
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

  rimo.insertAdjacentHTML = function(node, position, html) {
    node.insertAdjacentHTML(position, html)
  }

  rimo.textContent = function(node, text) {
    node.textContent = text
  }

  rimo.innerHTML = function(node, html) {
    node.innerHTML = html
  }

  rimo.outerHTML = function(node, html) {
    node.outerHTML = html
  }

  rimo.removeChildById = function(node, id) {
    const child = get_node(id)
    if (child) { node.removeChild(child) }
  }

  rimo.removeChildByIndex = function(node, index) {
    const child = node.childNodes.item(index)
    if (child) { node.removeChild(child) }
  }

  rimo.replaceChildById = function(node, html, id) {
    const old_child = get_node(id)
    if (old_child) {
      old_child.insertAdjacentHTML('beforebegin', html)
      old_child.parentNode.removeChild(old_child)
    }
  }

  rimo.replaceChildByIndex = function(node, html, index) {
    const old_child = node.childNodes.item(index)
    if (old_child) {
      rimo.insert(node, index, html)
      old_child.parentNode.removeChild(old_child)
    }
  }

  rimo.removeAttribute = function(node, attr) {
    node.removeAttribute(attr)
  }

  rimo.setAttribute = function(node, attr, value) {
    if (attr in node) {
      // some boolean values, like hidden, fail on setAttribute
      node[attr] = value
    } else {
      node.setAttribute(attr, value)
    }
  }

  rimo.addClass = function(node, classes) {
    // I won't support IE and Safari...
    // node.classList.add(...params.classes)
    node.classList.add.apply(node.classList, classes)
  }

  rimo.removeClass = function(node, classes) {
    // I won't support IE and Safari...
    // node.classList.remove(...params.classes)
    node.classList.remove.apply(node.classList, classes)
    if (node.classList.length == 0 && node.hasAttribute('class')) {
      node.removeAttribute('class')
    }
  }

  rimo.empty = function(node) {
    node.innerHTML = ''
  }

  rimo.getBoundingClientRect = function(node, reqid) {
    const rect = node.getBoundingClientRect()
    rimo.send_response(node, reqid, {
      bottom: rect.bottom,
      height: rect.height,
      left: rect.left,
      right: rect.right,
      top: rect.top,
      width: rect.width
    })
  }

  /* Event Control */
  rimo.click = function(node) {
    node.click()
  }

  /* Window Control */
  rimo.scroll = function(node, x, y){
    window.scrollTo(x, y)
  }

  rimo.scrollTo = function(node, x, y){
    window.scrollTo(x, y)
  }

  rimo.scrollBy = function(node, x, y){
    window.scrollBy(x, y)
  }

  rimo.scrollX = function(node, reqid){
    rimo.send_response(node, reqid, {x: window.scrollX})
  }

  rimo.scrollY = function(node, reqid){
    rimo.send_response(node, reqid, {y: window.scrollY})
  }

  rimo.log.log = function(level, message) {
    const msg = {
      type: 'log',
      level: level,
      message: message
    }

    if (rimo.settings.LOG_CONSOLE) {
      rimo.log.console(level, message)
    }
    rimo.push_msg(msg)
  }

  rimo.log.console = function(level, message) {
    if (rimo.log.level <= get_log_level(level) && 'console' in window) {
      console[level](rimo.settings.LOG_PREFIX + message)
    }
  }

  rimo.log.set_level = function(level) {
    rimo.log.level = get_log_level(level)
  }

  rimo.log.error = function(message) {
    rimo.log.log('error', message)
  }

  rimo.log.warn = function(message) {
    rimo.log.log('warn', message)
  }

  rimo.log.info = function(message) {
    rimo.log.log('info', message)
  }

  rimo.log.debug = function(message) {
    rimo.log.log('debug', message)
  }

  // Register object to global
  window.addEventListener('load', initialize, false)
  start_observer()
})(typeof window != 'undefined' ? window : void 0);
