import axel.services.net.server as serv
import axel.services.net.data_structures as ds
import axel.services.loader as loader
from axel.services.data_structures import LogEntry
import socket
from threading import Lock, Thread
from time import sleep
from functools import partial

lock = Lock()


def client_handler(conn: socket.socket, ip: str, cid: int, proxy: callable):
    try:
        s: serv.Server = proxy()
        data = conn.recv(1000)
        packet = ds.Packet().parse(data)
        entry = LogEntry(packet.value)
        lock.acquire()
        s.logs.append(entry)
        lock.release()

    except Exception as e:
        with open("aoeuaoeu.txt", "w") as f:
            f.write(f"exception {e} from {ip=}, {cid=}")


def store_logs(server: serv.Server):
    num = len(server.logs)
    count = 2
    while server.alive and count > 0:
        if num + server.log_diff > len(server.logs):
            # print("waiting", num, server.log_diff, len(server.logs))
            sleep(1)
        else:
            lock.acquire()
            try:
                loader.store_user_data("logs", server.logs)
            except Exception as e:
                with open("aoeuaoeu.txt", 'w') as f:
                    f.write(str(e))
            num = len(server.logs)
            # print("saveing", num)
            lock.release()
        count -= 1
    server.shutdown()


def simple_proxy(self, *args):
    return self


def start_server(port: int) -> serv.Server:
    current_data = loader.load_user_data("logs")
    server = serv.Server(port, client_handler)
    server.logs = current_data
    server.log_diff = 10
    server.proxy = partial(simple_proxy, server)
    t = Thread(target=store_logs, args=[server, ])
    t.start()
    return server


def main():
    port = serv.get_first_port_from(13131)
    current_data = loader.load_user_data("logs")
    server = serv.Server(port, client_handler)
    server.logs = current_data
    server.proxy = simple_proxy
    server.log_diff = 10
    t = Thread(target=store_logs, args=(server,))  # thread monitors the server
    t.start()
    # server.mainloop()
    sleep(5)
    server.shutdown()


if __name__ == '__main__':
    from pathlib import Path
    loader.DATA_PATH = Path("../dev_data")
    anchor = loader.get_anchor()
    main()
