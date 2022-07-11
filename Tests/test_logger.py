import axel.services.loader as loader
import axel.servers.logger as logger
from axel.services.net.server import get_first_port_from
import axel.services.net.data_structures as ds
from pathlib import Path
from time import sleep

ds.DEBUG = False
loader.DATA_PATH = Path("axel/dev_data")
loader.get_anchor()


def test_start_servers():
    port = get_first_port_from(13131)
    server = logger.start_server(port)
    sleep(.5)
    server.shutdown()
    sleep(.5)
    assert not any([a.is_alive() for a in server.running_threads]) and not server.alive

