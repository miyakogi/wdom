#!/usr/bin/env py.test
# -*- coding: utf-8 -*-

from os import path

from syncer import sync

from wdom.document import get_document
from wdom.testing import HTTPTestCase
from wdom import server


class TestServer(HTTPTestCase):
    def setUp(self):
        super().setUp()
        server.set_server_type('aiohttp')
        self.start()

    @sync
    async def test_mainpage(self):
        with self.assertLogs('wdom.server_aio', 'INFO'):
            response = await self.get('/')
        self.assertEqual(response.code, 200)
        self.assertRegex(
            response.body.decode('utf-8'),
            r'<!DOCTYPE html><html rimo_id="\d+">\s*<head rimo_id="\d+">\s*'
            r'.*<meta .*<title rimo_id="\d+">\s*W-DOM\s*</title>.*'
            r'</head>\s*<body.*>.*<script.*>.*</script>.*'
            r'</body>\s*</html>'
        )

    @sync
    async def test_tempfile(self):
        doc = get_document()
        self.assertTrue(path.exists(doc.tempdir))
        tmp = path.join(doc.tempdir, 'a.html')
        self.assertFalse(path.exists(tmp))
        with open(tmp, 'w') as f:
            f.write('test')
        self.assertTrue(path.exists(tmp))
        response = await self.get('/tmp/a.html')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), 'test')

    @sync
    async def test_tempfile_404(self):
        response = await self.get('/tmp/b.html')
        self.assertEqual(response.code, 404)
        response = await self.get('/tmp/a.html')
        self.assertEqual(response.code, 404)
