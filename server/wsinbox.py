"""Websocket inbox"""
import asyncio
import logging
import ssl

import websockets

from .client import Client

log = logging.getLogger(__name__)


class WSInbox(object):
    def __init__(self, world):
        super(WSInbox, self).__init__()
        self.world = world
        self.ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH
        )
        self.ssl_context.load_cert_chain(
            certfile='cert/cert.pem',
            keyfile='cert/key.pem'
        )
        self.ssl_context.verify_mode = ssl.CERT_OPTIONAL
        self.server = None

    async def handle_client(self, websocket, path):
        host, port = websocket.remote_address
        log.info(
            'Connected client from {}:{}'.format(host, port)
        )
        await Client(websocket, self.world).run()
        log.info(
            'Client from {}:{} disconnected'.format(host, port)
        )

    def run(self):
        self.server = asyncio.get_event_loop().run_until_complete(
            websockets.serve(
                self.handle_client, 'localhost', 8888, ssl=self.ssl_context
            )
        )

    def close(self):
        self.server.close()
        asyncio.get_event_loop().run_until_complete(self.server.wait_closed())
