"""Dispatching events to clients"""


class Dispatcher(object):
    clients = {}

    @staticmethod
    async def dispatch(atask):
        client = Dispatcher.clients.get(atask.player_id, None)
        await atask.run(client)
