import axel.services.net.server as serv
import socket
from time import sleep
import axel.services.net.data_structures as ds


def client_handle(conn: socket.socket, *args):

    w = ds.WrappedConnection(conn)

    while w.alive:
        w.parse_all()  # check for new
        while w.finished:
            message: ds.Packet = w.finished.pop(0)
            if message.data == "request content":
                with open("test_content_source.png", 'rb') as f:
                    data = f.read()
                w.send_obj(data)


def main():
    host_port = serv.get_first_port_from(13131)
    print(host_port)
    server = serv.Server(host_port, incoming_handler=client_handle)
    server.mainloop()


if __name__ == '__main__':
    main()
