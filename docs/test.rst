Test Utilities
==============

WDOM provides two Utility classes (``UITest`` and ``WDTest``) and some functions
for running test on browser with Selenium WebDriver.

UITest class
------------

``wdom.tests.ui.wd.UITest`` class is designed for end-to-end UI test, which is
useful for testing your app on browser. This class runs your app on subprocess
and prepare WebDriver for tests.

Usage
^^^^^

Example code using `py.test <http://pytest.org/>`_ as a test runner.

.. code-block:: python

    # in your_test_dir/conftest.py
    import pytest
    from wdom.tests.ui.wd import start_wd, close_wd

    @pytest.fixture(scope='session', autouse=True)
    def browser(request):
        start_wd()  # Start WebDriver for this session
        request.addfinalizer(close_wd)


    # in your test file
    from unittest import TestCase
    from wdom.misc import install_asyncio
    form wdom.tests.ui.wd import UITest

    def setUpModule():
        install_asyncio()  # force tornado to use asyncio

    class TestApp(UITest, TestCase):
        def setUp(self):
            # do some setup, if need.
            super().setUp()  # MUST call base class's setUp.

        def get_app() -> wdom.server.Application:
            # Prepare and return application you want to test
            return your_app

        def test_senario1(self):
            # Write your test here
            self.wd.get(self.url)  # you can access webdriver by self.wd

        def test_senario2(self):
            # Write your another test here
            ...


WDTest Class
------------

``WDTest`` class is design to test ``wdom`` itself. Its features might not be so
useful for library's users. ``WDTest`` class helps you to test your app by
directly controlling ``Node`` object on python, from test scripts in the same
process. This class is **Largely Experimental**.

``WDTest`` runs application server on the same process, which is running tests,
so that objects on the server can be directly controlled from test scripts.
WebDriver is run on subprocess, and controlled by passing messages on pipe.
This messaging process is wrapped by ``WDTest`` class and users don't need to
care it, but owing to this architecture, not all of the features of WebDriver
is available.

Usage
^^^^^

Example code using `py.test <http://pytest.org/>`_ as a test runner.

.. code-block:: python

    # in your_test_dir/conftest.py
    import pytest
    from wdom.tests.web.remote_browser import start_browser, close_browser

    @pytest.fixture(scope='session', autouse=True)
    def browser(request):
        start_browser()  # Start browser process for this session
        request.addfinalizer(close_browser)


    # in your test file
    from unittest import TestCase
    from wdom.tag import Div
    from wdom.document import get_document
    from wdom.server import get_app
    from wdom.tests.util import install_asyncio
    from wdom.tests.web.remote_browser import WDTest

    def setup_module():
        install_asyncio()  # force tornado to use asyncio module

    class TestYourApp(WDTest, TestCase):
        def get_app(self) -> wdom.server.Application:
            # Prepare and return application you want to test
            self.root_node = Div()
            self.root_node.textContent = 'RootNode'
            self.doc = get_document()
            self.doc.body.prepend(self.root_node)
            self.app = get_app(self.doc)
            return self.app

        def test_senario1(self):
            self.set_element(self.root)  # find and set element
            text = self.get_text()  # get text content of the target element
            self.assertEqual(text, 'RootNode')


For more examples, see wdom/tests/web and wdom/tests/ui directory.

.. automodule:: wdom.tests.ui.wd

   .. autoclass:: UITest
      :members:

.. automodule:: wdom.tests.web.remote_browser

   .. autoclass:: WDTest
      :members:
