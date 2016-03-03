Event
=====

先ほどの例ではブラウザに文字列を表示させるだけでしたが、今度はユーザーのアクションに反応して画面の表示が変化するアプリケーションを作ってみましょう。
具体的には、先ほど表示した文字列（``Hello,
MyApp!``）がクリックされるたびに反転するようにしてみましょう。

新しく ``reverse.py`` というファイルを作って、以下のように入力して下さい。

.. code-block:: python
    :linenos:

    import asyncio
    from wdom.misc import install_asyncio
    from wdom.tag import H1
    from wdom.document import get_document
    from wdom.server import get_app, start_server, stop_server

    install_asyncio()
    doc = get_document()

    text = H1('Hello, MyApp!', parent=doc.body)
    def reverse(data):
        rev_text = reversed(text.textContent)
        text.textContent = rev_text
    text.addEventListener('click', reverse)

    app = get_app(doc)

    loop = asyncio.get_event_loop()
    server = start_server(app=app, port=8888, loop=loop)
    loop.run_forever()

先ほどと同じように、``python reverse.py`` と実行してブラウザで
``http://localhost:8888/`` にアクセスして ``Hello, MyApp!``
をクリックしてみてください。
``!ppAyM ,olleH`` と反転したでしょうか？
さらにもう一度クリックすると元に戻るはずです。

Details
-------

それでは、コードを詳しく見ていきましょう。

ほとんどの部分は最初の例と同じなので、違う部分だけ説明します。
違いは10行目〜13行目の部分ですね。

Specify parent
--------------

まず、10行目の ``text = H1('Hello, MyApp!', parent=doc.body)`` では ``Hello,
MyApp!`` という文字列を含んだ ``H1`` 要素を作り、一旦 ``text``
変数に代入しています。
ここで、キーワード引数で ``parent=doc.body``
と指定していますが、このように指定することで自動的に親要素（``body``
要素）の末尾に要素を追加することができます。
これは ``doc.body.appendChild(text)`` とするのと等価です。

Event Listner
-------------

次に ``reverse`` 関数を定義しています。
これが ``H1`` 要素がクリックされた時に実行される処理になります。
引数の ``data``
にはイベントが発行された時に送られてきたデータが入りますが、今回は使っていません [#data]_。

textContent
^^^^^^^^^^^

``rev_text = reversed(text.textContent)`` では、``text`` （関数の外で定義された
``H1`` 要素）の ``textContent`` を取得して組み込み関数の ``reversed``
で反転しています。
要素の ``textContent`` 属性は要素内部のテキストだけを返す属性です。
子要素がある場合には、全ての子要素のテキストだけが抜き出されて連結されたものが返されます [#get_text_content]_。

次に ``text.textContent = rev_text`` で ``text``
内側のテキストを設定しています。
この時内部のテキストや子要素は全て削除され、新しいテキストが挿入されます [#set_text_content]_。

今回は説明のため二行に分けましたが、もちろんこれは
``text.textContent = reversed(text.textContent)``
として一行で処理することができます。

addEventListener
^^^^^^^^^^^^^^^^

14行目でイベント（``click``）が発生した時に ``reverse``
関数を実行するように登録しています。
この関数（``addEventListener``）の第一引数にはイベントの種類を文字列で指定します。
今回は要素がクリックされた時に実行される処理を登録するので ``'click'``
を指定しています。
第二引数にイベント時に処理を行う関数を登録します。
注意点は **関数オブジェクト** を登録するということです。
次のように関数オブジェクトにカッコをつけてしまうと、イベント発生時ではなくその場で関数が実行されエラーになってしまいます。 ::

    text.addEventListener('click', reverse())  # ERROR!!!

今回は一度 ``def`` 文で関数を定義しましたが、次のように無名関数をつかって関数の定義と登録を一気に行うことも可能です。 ::

    text.addEventListener('click',
        lambda data: text.textContent = reversed(text.textContent))

イベントのあつかいがわかったところで、次はユーザーからのテキスト入力を処理してみましょう。

.. rubric:: 脚注

.. [#data] 使わない場合でも関数呼び出し時に ``data``
    引数が渡されるので、引数を一つ取る関数として定義しないとエラーになってしまいます。
.. [#get_text_content] JavaScript で要素の ``textContent``
    属性にアクセスした時と同じ振る舞いです。
.. [#set_text_content] JavaScript で要素の ``textContent``
    に文字列を設定した時と同じ振る舞いです。
