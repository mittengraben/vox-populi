from setuptools import setup, find_packages


from server.version import version


setup(
    name="voxpopuli-server",
    version="{}.{}.{}".format(*version()),
    author="Mitten Graben",
    author_email="mr.cooldown@mail.ru",
    packages=find_packages(),
    install_requires=[
        "msgpack-python>=0.4.8",
        "websockets>=3.2"
    ],
    entry_points={
        "console_scripts": [
            "voxpopuli-server = "
            "server.server:Server.create_run",
        ],
    },
)
