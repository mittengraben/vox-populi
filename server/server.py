"""Main server class"""
import asyncio
import logging
import signal

from .world import World
from .wsinbox import WSInbox

log = logging.getLogger('main')


def _do_stop():
    asyncio.get_event_loop().stop()


class Server(object):
    def __init__(self):
        super(Server, self).__init__()

    def _setup(self):
        logformat = (
            '%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
        logging.basicConfig(level=logging.INFO, format=logformat)

        self.world = World()
        self.inbox = WSInbox(self.world)
        self.inbox.run()

    def run(self):
        self._setup()

        try:
            asyncio.get_event_loop().add_signal_handler(
                signal.SIGTERM, _do_stop
            )
            log.info('Starting server')
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.inbox.close()
            asyncio.get_event_loop().close()
            log.info('Done')

    @classmethod
    def create_run(cls):
        cls().run()


if __name__ == '__main__':
    Server.create_run()
