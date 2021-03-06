Basic DOM Features
==================

First Example
-------------

Program to show `"Hello, WDOM"` on browser is:

.. literalinclude:: samples/dom1.py

Save and execute the above code and access `http://localhost:8888` by browser.
Then, web page with `"Hello, WDOM"` will be shown.

.. currentmodule:: wdom.document

The four lines beginning from `document = get_document()` are very similar to
JavaScript.
`document` returned by :func:`get_document()` is a :class:`Document` node,
equivalent to `document` object in JavaScript on browsers.

`document.createElement('tag')` generates new element with the given tag.
`appendChild` method inserts the child node at the last of its child nodes.

Model of WDOM Elements
----------------------

GUI elements of the WDOM are composed of HTML tags (elements or nodes) on a
browser.
Usually they have one-by-one relationships;
thus `document.createElement('h1')` returns one WDOM element, and it is
rendered as an `<h1>` tag on a browser.
All WDOM elements have their own HTML representations, which can be obtained by
their `html` property.

APIs of WDOM elements are based on [DOM Living
Standard](https://dom.spec.whatwg.org/) and related standards ([HTML Living
Standard](https://html.spec.whatwg.org/multipage/), [CSS Object
Model](https://drafts.csswg.org/cssom/), [DOM
Parsing](https://w3c.github.io/DOM-Parsing/), and [Custom Elements in
WebComponents](http://w3c.github.io/webcomponents/spec/custom/)).

As elements are modeled by DOM, you can add/remove/replace them as same as the
ways in JavaScript on browsers. Currently, not all of the DOM features have
been implemented in WDOM, but lots of frequently-used methods/properties are
available. Implemented features can see :doc:`../reference` or list in [wiki at
gihub](https://github.com/miyakogi/wdom/wiki/Features).

### Create New Element

To make elements, WDOM provides two methods.

One is `document.createElement` mentioned above, and the other is to
instantiate classes defined in `wdom.tag` module. For details about the
`wdom.tag` module, see :doc:`wdom` section.

.. note:: Every element does not appear on browser until inserted to the DOM
    tree which roots on the document node returned by ``get_document()``.

### Append/Insert Node

To insert nodes on the DOM tree, use `appendChild` or `insertBefore` method.
`A.appendChild(B)` append the node B at the last of child nodes of the parent
node A. `A.insertBefore(B, C)` inserts new element B just before the reference
node C. The reference node C must be a child node of the node A.

These method names are quite long, so some methods specified in `DOM
specification`_ are also available on WDOM: `prepend`, `append`, `before`,
`after`, and `replaceWith`. Details about these methods are described in
:doc:`new_features` section.

### Remove Node

It is also able to remove child node from the DOM tree.

`A.removeChild(B)` removes the child node B from the parent node A. If B is
not a child node of A, it will raise Error.

More simple method `B.remove()` is also available, see :doc:`new_features`
section.

### Access Child/Parent/Sibling Nodes

`childNodes` property returns list-like live-object which contains its direct
child nodes. If the node does not have any child node, `childNodes` return
empty list-live object.

`firstChild` and `lastChild` property returns its first/last child node. On the
other way, `parentNode` property returns its parent node. `nextSibling` and
`previousSibling` returns its next/previous sibling node. If there is no
corresponding node, these properties return `None`.

These properties are same as JavaScript's DOM.

### Attributes

To get element's attributes like `class="..."` in HTML tag, use
`getAttribute('attr-name')` method. To set or change attribute's value, use
`setAttribute('attr-name', value)` method. And to remove an attribute, use
`removeAttribute` method.

To obtain all attributes set for the element, access `attributes` property.
This property returns dictionary-like abject `NamedNodeMap`. This object has
attributes and its value as `{'attr-name': value, ...}`.

### Special Attributes

Some attributes are accessible via special properties, for exmaple,
`element.id` returns its ID attribute. Available properties will be found in
:doc:`../reference` or [wiki page at
gihub](https://github.com/miyakogi/wdom/wiki/Features).

Attributes accessed via its properties return different types depending on its
property. For example, `element.id` return always string even if it is not set
(in case id is not set, `element.id` returns empty string, not None).
Similarly, `element.hidden` returns boolean (`True` or `False`) and
`element.style` returns `CSSStyleDeclaration`.

* References
    * [HTMLElement | MDN](https://developer.mozilla.org/en/docs/Web/API/HTMLElement)
    * [element.id | MDN](https://developer.mozilla.org/ja/docs/Web/API/Element/id)
    * [element.style | MDN](https://developer.mozilla.org/ja/docs/Web/API/HTMLElement/style)

### Style Attribute (CSSStyleDeclaration)

`element.style` returns `CSSStyleDeclaration` object, which provides access to
its css properties. For example, `element.style.color = 'red'` makes element's
color red.

Some css properties including hyphen (`-`) will be converted to CamelCase name.
For example, `background-color` will become `element.style.backgroundColor`.
For more examples, please see [CSS Properties
Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Properties_Reference)

Using HTML
----------

Making large applications with `appendChild` and `insertBefore` are quite
difficult. So writing HTML and parse it to WDOM elements is sometimes useful.

It can be done by `innerHTML` method, as same as JavaScript.
An example to make large list is below:

.. literalinclude:: samples/dom2.py

.. note::
    Assignment to ``innerHTML`` **removes all child nodes** and insert parsed
    elements.

Each child nodes can be accessed via `childNodes` property.

`insertAdjacentHTML({position}, {html})` also parses HTML and insert new
elements to the `position`. This method is also same as JavaScript's one, so
for details please see [MDN Element.insertAdjacentHTML()](https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML)
or `DOM specification`_.

`outerHTML` is not implemented in WDOM.

Event Handling
--------------

### Reverse Text on Click

WDOM's event handling is also same as JavaScript:

.. literalinclude:: samples/dom3.py

Run this code and click `"Hello, WDOM"`.
Then it will be reversed.
When clicked again, it will be reversed again and back to `"Hello, WDOM"`.

`addEventListener('event-type', handler)` method registers `handler` to the
given `event-type`. In the sample code, `rev_text` function is registered to
`click` event. Values available for event type are same as JavaScript's DOM, as
listed in [Event reference |
MDN](https://developer.mozilla.org/en-US/docs/Web/Events).

When the `h1` element is clicked, registered function `rev_text` is called with
a single argument, event, which is an :py:class:`Event` object, though it is
not used in the above example.

### User Input Event

The below example shows how to use event object:

.. literalinclude:: samples/dom4.py

In this sample, `textarea` element is added.
When user writes some text on the `textarea`, it will be shown as `h1` element.

In the `update` function, `event.currentTarget` has a reference to the element
which emitted the event, in this case it is a `textarea` element. And, as same
as JavaScript, a `textarea` element (and `input` element) contains its current
value in its `value` attribute.

At the moment `update` function is called, `textarea.value` is already
updated to the latest value. So the above code you can use `textarea.value`
instead of `event.currentTarget.value`.

In the sample code, setting its value using `h1` element's `textContent`.

.. _DOM specification: https://dom.spec.whatwg.org/
