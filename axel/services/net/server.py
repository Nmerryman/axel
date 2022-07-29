import threading
import time
import socket
from axel.services.net.data_structures import *
import psutil


class Server:
    """
    Model:
    each function gets handed proxy access to the main thread
    todo Consider any Packets moving around internally as always being command to free up another field
    todo Provide better ways to share data between clients
    """
    def __init__(self, root_port: int, incoming_handler):
        log("starting")
        self.alive = True
        self.root_port = root_port
        self.used_ports = [root_port]
        self.clients = {}  # {id: (conn, ip)}
        self.running_threads = []
        self.handle = incoming_handler
        self.enforce_broadcast_exclude = True

        self.running_threads.append(threading.Thread(target=self.root_thread))
        self.running_threads[0].start()
        log(f"started root thread and listening on 127.0.0.1:{self.root_port}")

    def mainloop(self):
        # The point of this to try to handle closing all threads when there is no custom server stuff needed.

        # This belongs to the server and will not get blocked or be involved with the sockets
        log("in mainloop")

        # Self kill test after enough time
        # while self.alive:
        #     if len(self.running_threads) > 2:
        #         self.shutdown()

        # Not sure if the mainloop needs to stay alive
        while self.alive:
            try:
                time.sleep(1)
            except:  # We want to catch ctrl-c
                self.alive = False

        # Kill the mainloop once all other threads are dead
        alive_count = {}
        for a in range(len(self.running_threads)):
            alive_count[a] = 0
        while True:
            all_dead = True
            for num_a, a in enumerate(self.running_threads):
                if a.is_alive():
                    log(f"Thread {num_a} is still alive")
                    all_dead = False
                    alive_count[num_a] += 1
                if alive_count[num_a] > 1:
                    if num_a == 0:
                        try:
                            self.pseudo_connection(self.root_port)
                        except ConnectionRefusedError:
                            log(f"Thread {num_a} refused new socket")  # we may be able to tell us this without needing the exception
                    else:
                        pass  # Not sure I can send into the cid connection
            if all_dead:
                break

            time.sleep(1)

    def root_thread(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", self.root_port))
        s.listen()
        while self.alive:
            conn, ip = s.accept()
            log(f"Connection from {ip}")
            if self.alive:
                t = threading.Thread(target=self.thread_base, args=(self.handle, conn, ip, len(self.running_threads), self.proxy))
                t.start()
                self.running_threads.append(t)

    def thread_base(self, func: callable, conn: socket.socket, ip: str, cid: int, proxy: callable):
        # Might not even need this base
        self.clients[cid] = (conn, ip)
        func(conn, ip, cid, proxy)
        self.clients.pop(cid)
        log(f"Ending {ip}")

    def proxy(self, command):
        # Allow a thread to use commands from the main thread (with permission)
        data = Packet().parse(command)
        if data.type == MessageType.command:
            if data.value == Commands.exit:
                self.alive = False
                self.shutdown()
            elif data.value == Commands.is_alive:
                return self.alive
            elif data.value == Commands.broadcast and data.extra:
                self.broadcast(data.generate(), exclude=int(data.extra))
            if data.value == Commands.request and data.extra == "self":
                return self

    def pseudo_connection(self, port):
        ks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ks.connect(("127.0.0.1", port))
        ks.close()

    def shutdown(self):
        # Kill what we can and then do some extra checking
        self.alive = False
        try:
            self.pseudo_connection(self.root_port)  # unblock listener thread
        except ConnectionRefusedError:
            pass

        # everything should clean itself up now. Not sure if I want to forcibly kill active threads

    def broadcast(self, data, exclude=-1):
        """
        Send Packet to all connections (except excluded)
        """
        for cid, (conn, ip) in self.clients.items():
            if cid != exclude or not self.enforce_broadcast_exclude:
                conn.sendall(data)

    def unblock(self, cid):
        if cid in self.clients.keys():
            conn = self.clients[cid][0]
            conn.sendall(Packet().generate())


def get_first_port_from(port: int, limit: int = 50000) -> int:

    used_ports = [a.laddr.port for a in psutil.net_connections()]
    while port in used_ports and port <= limit:
        port += 1
    if port == limit:
        raise ValueError("No valid port found")
    
    return port
