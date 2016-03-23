Data Binding
============

今度はテキストボックスを用意し、ユーザーの入力をそのまま表示するアプリケーションを作ってみましょう。
ついでに、クラスを作ってモジュール化してみましょう。

``data_binding.py`` というファイルを作って次のように入力してください。

.. code-block:: python
    :linenos:

    import asyncio
    from wdom.misc import install_asyncio
    from wdom.tag import H1, Div, H2, Input
    from wdom.document import get_document
    from wdom.server import get_app, start_server, stop_server


    class BindingView(Div):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.input = Input(parent=self)
            self.h2 = H2(parent=self)
            self.h2.style = 'border: dotted 1px #999;'
            self.input.addEventListener('input', self.update)

        def update(self, event):
            self.h2.textContent = event.value


    install_asyncio()
    doc = get_document()
    doc.body.appendChild(H1('Hello, MyApp!'))
    doc.body.appendChild(BindingView())
    app = get_app(doc)

    loop = asyncio.get_event_loop()
    server = start_server(app=app, port=8888, loop=loop)
    loop.run_forever()
