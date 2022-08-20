import axel.services.net.server as serv
import socket
from time import sleep, time
import axel.services.net.data_structures as ds
from axel.services.data_structures import Client, FileToken
from threading import Lock, Thread


lock = Lock()


def send_single(address: str, port: int, obj):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    w = ds.WrappedConnection(s)

    w.send_obj(obj)


def client_handle(conn: socket.socket, ip: str, cid: int, proxy: callable):

    w = ds.WrappedConnection(conn)
    s: DServer = proxy()

    while w.alive and s.alive:
        w.parse_all()  # check for new
        while w.finished:
            message: ds.Packet = w.finished.pop(0)
            if isinstance(message, ds.Packet):
                if message.type == "register" and message.value == "sharing server":  # We are just checking for proper packets
                    client = Client(*w.conn.getpeername())
                    print("peer", w.conn.getpeername())
                    print("sock", w.conn.getsockname())
                    print("ip", ip)
                    if client not in s.sharing_servers:
                        print(f"REPLACED {client=}")
                        with lock:
                            s.sharing_servers.clear()
                            s.sharing_servers.append(client)
                        w.send_obj(ds.Packet("status", "ok"))
                    else:
                        w.send_obj(ds.Packet("status", "error", "No clients found"))
                elif message.type == "request" and message.value == "sharing server" and s.sharing_servers:
                    w.send_obj(ds.Packet("server info", s.sharing_servers[0].dumps()))
                elif message.type == "request" and message.value == "content" and s.sharing_servers:
                    token = "aaaaaaaaaaaaaaaa"
                    file_hash = "81c27e1da04d306ec6b3b832002f7fa02951e181cbb4e62a779f1ec29627f0c0"
                    host_s = s.sharing_servers[0]
                    send_single(host_s.ip, host_s.port, ds.Packet("add token", FileToken(file_hash, token, time() + 1000).dumps()))
                    w.send_obj(ds.Packet("content source", Client(host_s.ip, host_s.port).dumps(), token))
                else:
                    print(message, s.sharing_servers)
                    w.send_obj(ds.Packet("status", "error", "No matching type"))


class DServer(serv.Server):
    
    def __init__(self, root_port: int, incoming_handler):
        self.sharing_servers: list[Client] = []
        super().__init__(root_port, incoming_handler)

    def proxy(self, *args):
        return self


def main():
    host_port = serv.get_first_port_from(13131)
    print(host_port)
    server = DServer(host_port, incoming_handler=client_handle)
    server.mainloop()


if __name__ == '__main__':
    main()
