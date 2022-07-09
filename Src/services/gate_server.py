import net.server as BaseServer
from net.data_structures import DEBUG
import psutil
import socket
import time

# This service is designed to allow more (unpriveleded) servers to provide access points into the network


def gate_handler(conn: socket.socket, ip: str, cid: int, proxy_func: callable):
    pass


def main(is_root=False, forced_port=None):
    """
    Decide on the server port
    :param is_root:
    :param forced_port:
    :return:
    """
    my_port = 13000
    used_ports = [a.laddr.port for a in psutil.net_connections()]
    if forced_port:
        my_port = forced_port
        if my_port in used_ports:
            raise ValueError(f"Port {forced_port} is already in use.")
    else:
        while my_port in used_ports and my_port < 30000:
            my_port += 1
        if my_port == 30000:
            raise ValueError("No open port found")

    server = BaseServer.Server(my_port, gate_handler)
    time.sleep(3)
    server.shutdown()


if __name__ == '__main__':
    DEBUG = True
    main(forced_port=13000)

