import axel.services.net.server as serv
import socket
from time import sleep
import axel.services.net.data_structures as ds


def client_handle(conn: socket.socket, ip: str, cid: int, proxy: callable):
    sleep(1)
    w = ds.WrappedConnection(conn)
    w.send_obj(ds.Packet("Hello World!"))
    w.close()


def main():
    host_port = serv.get_first_port_from(13131)
    print(host_port)
    server = serv.Server(host_port, incoming_handler=client_handle)
    server.mainloop()


if __name__ == '__main__':
    main()
