Newest DOM Features
-------------------

Some new features of DOM, which have not been implemented yet on browsers are
available on WDOM.

ParentNode and ChildNode Interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``appendChild`` method add only one child node, but ``append`` method can append
multiple nodes at once. Furthermore, strings are also available (strings are
automatically converted to Text Node).

.. literalinclude:: samples/new1.py

Similarly, ``prepend``, ``after``, and ``before`` methods are available.
Furthermore, ``remove``, ``replaceWith``, ``children``, ``firstElementChild``,
and ``lastElementChild`` methods are also available on WDOM.

Internally, these methods update view on the browser at once, so using these
methods usually result in better performance.

* References

    * `ParentNode | DOM Standard <https://dom.spec.whatwg.org/#interface-parentnode>`_
    * `NonDocumentTypeChildNode | DOM Standard <https://dom.spec.whatwg.org/#nondocumenttypechildnode>`_
    * `ChildNode | DOM Standard <https://dom.spec.whatwg.org/#interface-childnode>`_

Custom Element
^^^^^^^^^^^^^^

WDOM provides limited supports on custom elements (experimentally).

User Defined Custom Tags
~~~~~~~~~~~~~~~~~~~~~~~~

As an example, define ``MyElement`` as a custom tag (``<my-element>``).

.. literalinclude:: samples/new2.py

Difference is a class variable ``tag = 'my-element'``.

To register ``MyElement`` class as a custom tag, use
``document.defaultView.customElements.define()`` method.

.. note:: Formarly, ``document.registerElement`` method was used to define custom tags,
    but in the `latest specification
    <http://w3c.github.io/webcomponents/spec/custom/>`_ uses
    ``customElements.define`` method to reagister custom tags.
    WDOM supports the same method as the latest specification.

``document.defaultView`` property returns a reference to the window object,
which is same as the ``window`` object of JavaScript on browsers.

Now you can use the registered custom tag from
``document.createElement('my-element')`` or ``innerHTML =
'<my-element></my-element>>'.
Both these methods return new instance of ``MyElement``

Extended Custom Tags
~~~~~~~~~~~~~~~~~~~~

WDOM supports to extend existing tags with ``is`` attribute.

For example, to define ``MyButton`` or ``DefaultButton`` as a custom tag:

.. literalinclude:: samples/new3.py

On the class statements, add class variable ``is_`` and specify the name of the
custom tag.
Class variable ``tag`` is a tag name to be extended, but in the above example,
it is already defined in ``Button`` class.

When registering the custom tag, pass the name (value of ``is_``) at the first
argument to ``customElements.define`` and pass dictionary which contains
``'extends'`` field to specify the tag name to be extended, at the third
argument.

After the registration, an HTML like ``<button is="my-button">`` will be parsed
to an instance of ``MyElement``, and ``<button is="default-button">`` to
``DefaultButton``.

.. caution::
    Register custom tags as early as possible.
    If the instance was generated before registering it, it becomes different
    class.
    When the ``customElements.define`` is called and registerd, WDOM will try to
    update the class of existing instances but ``__init__`` will not be not
    called.

    Additionally, changing ``is`` attribute of the existing instances, likely
    ``element.setAttribute('is', '...')``, do not change its class currently.

    In future, `Lifecycle callback methods
    <http://www.html5rocks.com/en/tutorials/webcomponents/customelements/#lifecycle>`_
    or silimar features will be implemented, but still it's safer to register
    custom tags before instanciate it.
