import net.server
import psutil
import socket


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

    server = net.server.Server(my_port, gate_handler)


if __name__ == '__main__':
    main(forced_port=13000)

