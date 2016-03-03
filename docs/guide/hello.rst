First Example
=============

第一歩として、 ``Hello, MyApp!``
というテキストを表示するアプリケーションを作ってみましょう。

好きなテキストエディタで ``hello.py``
というファイルを作り、次のように入力してください。

.. code-block:: python
    :linenos:

    import asyncio
    from wdom.misc import install_asyncio
    from wdom.tag import H1
    from wdom.document import get_document
    from wdom.server import get_app, start_server, stop_server

    install_asyncio()
    doc = get_document()
    doc.body.appendChild(H1('Hello, MyApp!'))
    app = get_app(doc)

    loop = asyncio.get_event_loop()
    server = start_server(app=app, port=8888, loop=loop)
    loop.run_forever()

このファイルを ``python3 hello.py``
としてコマンドラインから実行し、ブラウザを開いて ``http://localhost:8888/``
にアクセスしてください。
以下のように ``Hello, MyApp!`` と表示されているでしょうか？

確認ができたらアプリケーションを停止させましょう。
先ほどスクリプトを実行したターミナル上で ``Ctrl+C`` を押すと停止します。

Details
-------

このコードの内容について詳しくみていきましょう。

まず、最初の ``install_asyncio()`` はおまじないだと思って下さい [#install_asyncio]_。

Document Object
^^^^^^^^^^^^^^^

二行目の ``doc = get_document()`` でドキュメントオブジェクトを取得しています。
このオブジェクトはブラウザ上の JavaScript での ``document`` に相当します。

appendChild
^^^^^^^^^^^

三行目の ``doc.body.appendChild(H1('Hello, MyApp!'))``
では、内側にテキストとして ``'Hello, MyApp!'`` を含んだ ``H1``
要素を作り、 ``document`` の ``body`` 要素の末尾に追加（``appendChild``）しています。
この動作は JavaScript を使ったことがある方には馴染みがあるのではないでしょうか。

この時点で、ブラウザ上に描画される HTML は概ね次のようになっています。

.. code-block:: html

    <html>
    <head>
    ...
    </head>
    <body>
        <h1>Hello, MyApp!</h1>
    </body>
    </html>

どのような HTML になっているかは ``print(doc.render())`` で確認できます。
ヘッダーや ``id``
属性などが追加されているので全く同じではありませんが、おおよその内容は確認できるでしょう。
また、特定の要素と内部の HTML だけを確認したい場合は、要素の ``html``
属性にアクセスすることで確認できます。
上記の例では ``print(doc.body.html)`` とすると ``body``
要素の内容（``<body>``〜``</body>``）だけが表示されます。

Get Application
^^^^^^^^^^^^^^^

これでブラウザに表示する内容は用意出来たので、これを表示するアプリケーション・サーバーを立ち上げます。

``app = get_app(doc)`` でアプリケーションを取得しています。
第一引数にはアプリケーションで表示する内容（``document``）を指定します。

次に ``loop = asyncio.get_event_loop()`` でイベントループを取得しています。
これもおまじないです。

Run Server
^^^^^^^^^^

``server = start_server(app=app, port=8888, loop=loop)`` でアプリケーション、サーバーのポート番号（ここでは8888）、イベントループを指定してサーバーを実行しています。

そのままだとアプリケーションが終了してしまうので、``loop.run_forever()``
として実行を続けさせています。

それでは、次のページでイベントを使ってGUIアプリケーションらしくしていきましょう！

.. rubric:: 脚注

.. [#install_asyncio] WDOMでウェブサーバーとして利用している tornado は
    独自の並列処理を実装しています。しかし、WDOMでは基本的に並列処理に
    python 3.4 で導入された asyncio を使っているので、とりあえずイベントループの
    相乗りをするためにこの処理を入れています。
    詳細は `tornado のドキュメント <http://www.tornadoweb.org/en/stable/asyncio.html>`_
    を参照してください。
