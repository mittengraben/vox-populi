"""Main server class"""
import argparse
import asyncio
import json
import logging
import signal

from .version import version
from .world import World
from .wsinbox import WSInbox

log = logging.getLogger('main')


def _do_stop():
    asyncio.get_event_loop().stop()


class Server(object):
    def __init__(self):
        super(Server, self).__init__()

    def _setup(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--config',
            default='./etc/config.json',
        )
        parser.add_argument(
            '--version',
            action='version',
            version='v{}.{}.{}'.format(*version())
        )
        args = parser.parse_args()

        with open(args.config, 'r') as config_file:
            conf = json.load(config_file)

        logformat = (
            '%(process)d:%(asctime)s:%(levelname)s:%(name)s:%(message)s'
        )
        logging.basicConfig(level=logging.INFO, format=logformat)

        self.world = World(conf)
        self.inbox = WSInbox(conf, self.world)
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
            self.world.dispose()
            self.inbox.close()
            asyncio.get_event_loop().close()
            log.info('Done')

    @classmethod
    def create_run(cls):
        cls().run()


if __name__ == '__main__':
    Server.create_run()
