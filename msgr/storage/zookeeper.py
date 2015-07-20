from kazoo.client import KazooClient

from msgr import settings


zk = KazooClient(hosts=settings.ZK['URL'])


def init():
    zk.start()
