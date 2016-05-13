Basic DOM Features
------------------

First Example
^^^^^^^^^^^^^

Program to show ``"Hello, WDOM"`` on browser is:

.. literalinclude:: samples/dom1.py

Save and execute code and access ``http://localhost:8888`` by browser.
Then, web page with ``"Hello, WDOM"`` will be shown.

The four lines beginning from ``document = get_document()`` are very similar to
JavaScript.
``document`` returned by ``get_document()`` is a Document Node, equivalent to
``document`` object in JavaScript on browsers.
``document.createElement('{tag-name}')`` generates new element with the given
tag-name.
``appendChild`` method inserts the child node at last.
Not used in the sample code, by using ``removeChild`` method, one can remove the
child node.

Model of WDOM Elements
^^^^^^^^^^^^^^^^^^^^^^

GUI elements of the WDOM are composed of HTML tags (elements or nodes) on a
browser.
Usually they have one-by-one relationships:
thus ``document.createElement('h1')`` returns one WDOM element, and it is
rendered as an ``<h1>`` tag on a browser.
All WDOM elements have their own HTML representations, which can be obtained by
their ``html`` property.

Elements created by WDOM are all based on `DOM Living Standard
<https://dom.spec.whatwg.org/>`_ and related standards (`HTML Living Standard
<https://html.spec.whatwg.org/multipage/>`_, `CSS Object Model
<https://drafts.csswg.org/cssom/>`_, `DOM Parsing
<https://w3c.github.io/DOM-Parsing/>`_, and `Custom Elements in WebComponents
<http://w3c.github.io/webcomponents/spec/custom/>`_).

As elements are modeled by DOM, you can add/remove/replace them as same as the
way in JavaScript on browsers.
Currently, not all of DOM features have been implemented in WDOM, but lots of
frequently-used methods/properties are available.
Implemented features are listed in `wiki pages at gihub
<https://github.com/miyakogi/wdom/wiki/Features>`_.

Create New Element
~~~~~~~~~~~~~~~~~~

To make elements, WDOM provides two methods.
One is ``document.createElement`` mentioned above, and the other is to
instantiate classes defined in ``wdom.tag`` module.
For details about the ``wdom.tag`` module, see :doc:`wdom` section.

.. note:: Every element does not appear on browser until inserted to the DOM
    tree which roots on the document node returned by ``get_document()``.

Append/Insert Node
~~~~~~~~~~~~~~~~~~

To insert nodes on the DOM tree, use ``appendChild`` or ``insertBefore`` method.
``A.appendChild(B)`` append the node B at last of child nodes of the parent node A.
``A.insertBefore(B, C)`` inserts new element B just before the reference node C.
The reference node C must be a child node of the parent node A.

These method names are quite long, so some methods specified in `DOM
specification`_ are also available on WDOM: ``prepend``, ``append``, ``before``,
``after``, and ``replaceWith``.
Details about these methods are described in :doc:`new_features` section.

Remove Node
~~~~~~~~~~~

It is also able to remove child node from the DOM tree.
``A.removeChild(B)`` removes the child node B from the parent node A.
If B is not a child node of A, it will raise Error.

More simple method ``B.remove()`` is also available, see :doc:`new_features`
section.

Access Child/Parent Nodes
~~~~~~~~~~~~~~~~~~~~~~~~~

``childNodes`` property returns list-like live-object which contains its direct
child nodes.
``firstChild`` and ``lastChild`` property returns its first/last child node.

On the other way, ``parentNode`` property returns its parent node.
These properties are same as JavaScript's DOM.

Attributes
~~~~~~~~~~

To get/set element's attributes like ``class="..."`` in HTML tag, use
``getAttribute/setAttribute`` method.

Some attributes are accessible via special properties, for exmaple, ``A.id``
returns its ID attribute.
Available properties will be found in `wiki page at gihub
<https://github.com/miyakogi/wdom/wiki/Features>`_.

Using HTML
^^^^^^^^^^

Making large applications with ``appendChild`` and ``insertBefore`` are quite
difficult.
So writing HTML and parse it to WDOM elements is sometimes useful.

It can be done by ``innerHTML`` method, as same as JavaScript.
For example, an example to make large list is below:

.. literalinclude:: samples/dom2.py

.. note::
    Assignment to ``innerHTML`` **removes all child nodes** and insert parsed
    elements.

Each child nodes can be accessed via ``childNodes`` property, which returns
list-like live-object, but not able to modify its values.
Similar to JavaScript, ``firstChild`` and ``lastChild`` property provides
reference to the first/last child node.

``insertAdjacentHTML({position}, {html})`` also parses HTML and insert new
elements to the ``position``.
This method is also same as JavaScript's one, so for details please see `Element.insertAdjacentHTML() | MDN <https://developer.mozilla.org/en-US/docs/Web/API/Element/insertAdjacentHTML>`_ or `DOM specification`_.

``outerHTML`` is not implemented.

Events
^^^^^^

Reverse Text on Click
~~~~~~~~~~~~~~~~~~~~~

WDOM's event handling is also same as JavaScript:

.. literalinclude:: samples/dom3.py

Run this code and click ``"Hello, WDOM"``.
Then it will be reversed.
When clicked again, it will be reversed again and back to ``"Hello, WDOM"``.

``addEventListener('{event-type}', {handler})`` method registers ``handler`` to
the given ``event-type``.
In the sample code, ``rev_text`` function is registered to ``click`` event.
Values available for event type are same as JavaScript's DOM, for example, it is
listed at `Event reference | MDN
<https://developer.mozilla.org/en-US/docs/Web/Events>`_.

When the ``h1`` element is clicked, registered function ``rev_text`` is called with
a single argument, event, which is an Event object, though it is not used in the
sample code.

User Input Event
~~~~~~~~~~~~~~~~

The below sample shows how to use event object:

.. literalinclude:: samples/dom4.py

In this sample, ``textarea`` element is added.
When user inputs some text on the ``textarea``, it will be shown as ``h1`` element.

In the ``update`` function, ``event.target`` has a reference to the element
which emitted the event, in this case it is a ``textarea`` element.
And, as same as JavaScript, a ``textarea`` element (and ``input`` element) contains
its current value at ``value`` attribute.
In the sample code, setting its value to ``h1`` element's ``textContent``.


.. _DOM specification: https://dom.spec.whatwg.org/
