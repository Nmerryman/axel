import axel.services.loader as loader
import axel.servers.logger as logger
from axel.services.net.server import get_first_port_from
import axel.services.net.data_structures as ds
from axel.services.data_structures import LogEntry
from pathlib import Path
from time import sleep
import socket

ds.DEBUG = False
loader.DATA_PATH = Path("axel/dev_data")
loader.get_anchor()
global_serv = ""


def test_start_servers():
    # Verify the server can start and end
    port = get_first_port_from(13131)
    server = logger.start_server(port)
    sleep(.25)  # There seems to be some startup time for these
    server.shutdown()
    sleep(.25)
    assert not any([a.is_alive() for a in server.running_threads]) and not server.alive


def test_store_entry():
    global global_serv
    port = get_first_port_from(13131)
    server = logger.start_server(port)
    global_serv = server
    sleep(.25)
    num = len(server.logs)
    start = loader.load_user_data("logs")
    # Create client and send test packet
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", port))
    entry = LogEntry("User", "Hello World!")
    packet = ds.Packet("log", entry.dumps())
    client.sendall(packet.generate())
    sleep(.25)

    assert num < len(server.logs)  # check to see that entry got stored
    current = loader.load_user_data("logs")
    assert start == current
    server.log_diff = 1
    sleep(1)
    current = loader.load_user_data("logs")
    assert start != current  # make sure the auto saver feature works

    server.shutdown()


try:
    global_serv.shutdown()
except:
    pass

