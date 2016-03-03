Test Utilities
==============

``wdom.tests.util`` module provides two Utility classes (``UITest`` and
``WDTest``) and some functions for running test on browser with Selenium
WebDriver. These test classes inherit ``unittest.TestCase``.

UITest class
------------

``UITest`` class is designed for end-to-end UI test, which is useful for testing
your app on browser. This class runs your app on subprocess and prepare
WebDriver for tests.

Usage
^^^^^

Example code using `py.test <http://pytest.org/>`_ as a test runner::

    from wdom.tests.util import UITest, install_asyncio, get_browser

    def setup_module():
        install_asyncio()  # force tornado to use asyncio module

    def teardown_module():
        wd = get_browser()  # get running webdriver
        wd.close()  # terminate webdriver

    class TestApp(UITest):
        def setUp(self):
            # do some setup, if need.
            super().setUp()  # MUST call base class's setUp.

        def get_app() -> wdom.server.Application:
            # Prepare and return application you want to test
            return your_app

        def test_senario1(self):
            # Write your test here
            self.wd.get(self.url)  # you can access webdriver by self.wd
            self.get(self.url)  # 

        def test_senario2(self):
            # Write your another test here
            ...


WDTest Class
------------

``WDTest`` class is design to test ``wdom.py`` itself. Its features might
not be so useful for library's users. ``WDTest`` class helps you to test your
app by directly controlling ``Node`` object on python, from test scripts in the
same process. This class is **Largely Experimental**.

``WDTest`` runs application server on the same process, which is running tests,
so that objects on the server can be directly controlled from test scripts.
WebDriver is run on subprocess, and controlled by passing messages on pipe.
This messaging process is wrapped by ``WDTest`` class and users don't need to
care it, but owing to this architecture, not all of the features of WebDriver
is available.

Usage
^^^^^

Example code using `py.test <http://pytest.org/>`_ as a test runner::

    from wdom.tests.util import WDTest
    from wdom.tests.util import install_asyncio, start_browser, close_browser

    def setup_module():
        install_asyncio()  # force tornado to use asyncio module
        start_browser()  # start browser on subprocess

    def teardown_module():
        close_browser()  # close browser's process

    class TestYourApp(WDTest):
        def get_app(self) -> wdom.server.Application:
            # Prepare and return application you want to test
            self.root_node = wdom.dom.Node()
            self.root_node.textContent = 'RootNode'
            self.doc = wdom.view.get_document()
            self.doc.set_body(self.root_node)
            self.app = wdom.server.get_app(document=self.doc)
            return self.app

        def test_senario1(self):
            self.set_element(self.root)  # find and set element
            text = self.get_text()  # get text content of the target element
            assert text == 'RootNode'


For more examples, see wdon/tests/test_dom_web.py.

.. automodule:: wdom.tests.web.remote_browser

   .. autoclass:: UITest
      :members:

   .. autoclass:: WDTest
      :members:
