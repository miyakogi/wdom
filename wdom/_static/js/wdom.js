/* Wdom v0.0.1 alpha, @lisence MIT, copyright 2016, miyakogi */

;(function(window, undefined){
  'use strict';
  // Define global object
  var W = { version: '0.0.1', settings: {}}
  var Wlog = { loglevel: 0 }
  var config_prefix = 'WDOM_'

  var log_levels = {
    FATAL: 50,
    CRITICAL: 50,
    ERROR: 40,
    WARNING: 30,
    WARN: 30,
    INFO: 20,
    DEBUG: 10,
    NOTSET: 0,
  }

  function get_log_level(level) {
    if (typeof level === 'number'){
      return level
    }

    if (typeof level === 'string') {
      var s = level.toUpperCase()
      if (s in log_levels) {
        return log_levels[s]
      }
    }

    // Get unknown log level
    console.warn(W.settings.LOG_PREFIX + 'unknown log level: ', level)
    return 0
  }

  function set_default(key, defval) {
    if (config_prefix + key in window) {
      W.settings[key] = window[config_prefix + key]
    } else {
      W.settings[key] = defval
    }
  }

  function get_node(id) {
    return document.getElementById(id)
  }

  function ws_onmessage(e) {
    var msg = JSON.parse(e.data)
    console.log(msg)
    var elm = get_node(msg.id)
    if (!elm) {
      // node may not have been mounted yet. retry 100ms later.
      setTimeout(function() {
        var elm = get_node(msg.id)
        if (!elm) {
          // node not found. send warning.
          Wlog.console('warn', 'gat message to unknown node.\n Message: ' + msg)
          Wlog.warn('unknown node: id=' + msg.id + ', tag=' + msg.tag + ', method=' + msg.method)
        } else {
          W.exec(elm, msg.method, msg.params)
        }
      }, 100)
    } else {
      W.exec(elm, msg.method, msg.params)
    }
  }

  function ws_onclose() {
    function reload(){
      location.reload()
    }

    if (W.settings.AUTORELOAD) {
      Wlog.console('info', 'RootWS closed, reloading page...')
      setTimeout(reload, W.settings.RELOAD_WAIT)
    } else {
      Wlog.console('RootWS CLOSED');
    }
  }

  function initialize() {
    // Define default variables
    var __ws_url = 'ws://' + location.host + '/wdom_ws'
    set_default('DEBUG', false)
    set_default('AUTORELOAD', false)
    set_default('RELOAD_WAIT', 500)
    set_default('LOG_LEVEL', 'WARN')
    set_default('LOG_PREFIX', 'WDOM: ')
    set_default('LOG_CONSOLE', false)
    set_default('WS_URL', __ws_url)
    console.log(W.settings)

    Wlog.set_loglevel(W.settings.LOG_LEVEL)

    // Make root WebScoket connection
    W.ws = new WebSocket(W.settings.WS_URL)
    W.ws.onmessage = ws_onmessage
    W.ws.onclose = ws_onclose
  }

  W.exec = function(node, method, params) {
    // Execute fucntion with msg
    W[method](node, params)
  }

  /* Event contrall */
  // emit events to python
  // find better name...
  W.send_event = function(node, event, data) {
    var msg = JSON.stringify({
      type: 'event',
      id: node.id,
      event: event,
      data: data
    })
    Wlog.debug(msg)
    W.ws.send(msg)
  }

  /* Event handlers */
  W.onclick = function(node) {
    W.send_event(node, 'click')
  }

  W.onchange = function(node) {
    W.send_event(
      node,
      'change',
      {
        checked: node.checked,
        value: node.value,
      }
    )
  }

  W.oninput = function(node) {
    W.send_event(
      node,
      'input',
      {
        checked: node.checked,
        value: node.value,
      }
    )
  }

  W.addEventListener = function(node, params) {
    var e = 'on' + params.event
    node.addEventListener(e, function() { W[e](node) })
  }

  /* DOM contrall */
  W.insert = function(node, params) {
    if (!node.hasChildNodes() || params.index >= node.childNodes.length) {
      W.append(node, params)
    } else {
      node.childNodes[Number(params.index)].insertAdjacentHTML(
        'beforebegin',
        params.html
      )
    }
  }

  W.appendChild = function(node, params) {
    node.insertAdjacentHTML('beforeend', params.html)
  }

  W.insertBefore = function(node, params) {
    var c = document.getElementById(params.id)
    c.insertAdjacentHTML('beforebegin', params.html)
  }

  W.removeChild = function(node, params) {
    var child = document.getElementById(params.id)
    node.removeChild(child)
  }

  W.replaceChild = function(node, params) {
    var old_child = document.getElementById(params.id)
    old_child.insertAdjacentHTML('beforebegin', params.html)
  }

  W.removeAttribute = function(node, params) {
    node.removeAttribute(params.attr)
  }

  W.setAttribute = function(node, params) {
    var value = params.value
    if (typeof value === 'string'){
      if (value === 'true') {
        value = true
      } else if (value === 'false') {
        value = false
      }
    }
    if (params.attr in node) {
      node[params.attr] = value
    } else {
      node.setAttribute(params.attr, value)
    }
  }

  W.addClass = function(node, params) {
    if (node.classList) {
      node.classList.add(params.class)
    } else {
      node.className += ' ' + params.class
    }
  }

  W.removeClass = function(node, params) {
    if (node.classList) {
      node.classList.remove(params.class)
    } else {
      node.className = node.className.replace(params.class, '')
    }
  }

  W.empty = function(node) {
    node.innerHTML = ''
  }

  Wlog.log = function(level, message, retry) {
    var msg = JSON.stringify({
      type: 'log',
      level: level,
      message: message
    })

    if (W.settings.LOG_CONSOLE) {
      Wlog.console(level, message)
    }

    if (!W.ws.OPEN) { 
      retry = retry ? retry + 1 : 1
      if (retry < 5) {
        setTimeout(function() { Wlog.log(level, message, retry) }, 200)
      } else {
        setTimeout(function() { W.ws.send(msg) }, 200)
      }
    } else {
      W.ws.send(msg)
    }
  }

  Wlog.console = function(level, message) {
    if (Wlog.loglevel <= get_log_level(level)) {
      console[level](W.settings.LOG_PREFIX + message)
    }
  }

  Wlog.set_loglevel = function(level) {
    Wlog.loglevel = get_log_level(level)
  }

  Wlog.error = function(message) {
    Wlog.log('error', message)
  }

  Wlog.warn = function(message) {
    Wlog.log('warn', message)
  }

  Wlog.info = function(message) {
    Wlog.log('info', message)
  }

  Wlog.debug = function(message) {
    Wlog.log('debug', message)
  }

  // Register object to global
  window['W'] = W
  window['Wlog'] = Wlog
  window.addEventListener('load', initialize)

})(typeof window != 'undefined' ? window : void 0);
