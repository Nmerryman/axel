import axel.services.loader as loader
import axel.services.data_structures as ds
import axel.services.net.server as serv
import axel.services.net.data_structures as ns
from pathlib import Path
from hashlib import sha256
import os
import time
import socket
from threading import Lock


lock = Lock()


def hash_file(path: Path):
    h = sha256()
    buffer = h.block_size * 1_000
    with open(path, 'rb') as f:
        while chunk := f.read(buffer):
            h.update(chunk)
    return h.hexdigest()


def explore_storage():
    names = os.listdir(loader.DATA_PATH / "storage")
    files = []
    for a in names:
        fp = loader.DATA_PATH / "storage" / a
        files.append(ds.FileIndex(a, hash_file(fp), os.path.getsize(fp), time.time()))
    return files


class ShareServ(serv.Server):

    def __init__(self, root_port: int, file_cache: list[ds.FileIndex], tokens_cache: list[ds.FileToken]):
        super().__init__(root_port, self.client_handle)
        self.index_files: list[ds.FileIndex] = file_cache
        self.index_tokens: list[ds.FileToken] = tokens_cache

    def proxy(self, *args):
        return self

    @staticmethod
    def client_handle(conn: socket.socket, ip: str, cid: int, proxy: callable):
        wconn = ns.WrappedConnection(conn)
        while wconn.alive and not wconn.finished:
            wconn.parse_all()

            if wconn.alive and not wconn.finished:
                time.sleep(1)  # We may not care about this, but its to lessen the load on the system

            for a in wconn.finished:
                if isinstance(a, ns.Packet):  # we only want packets in this filter
                    if a.type == "request":
                        test_file = loader.DATA_PATH / "storage" / "test_content_source.png"
                        with open(test_file, 'rb') as f:
                            data = f.read()
                        wconn.send_obj(data)
                    elif a.type == "check files":
                        with lock:
                            s: ShareServ = proxy()
                            s.index_files = explore_storage()
                        wconn.send_obj(ns.Packet("status", "ok", len(s.index_files)))
                    elif a.type == "add token":
                        with lock:
                            s: ShareServ = proxy()
                            s.index_tokens.append(ds.FileToken(a.value))
                        wconn.send_obj(ns.Packet("status", "ok", len(s.index_tokens)))
                    else:
                        wconn.send_obj(ns.Packet("status", "error"))
                else:
                    wconn.send_obj(ns.Packet("status", "error", "Only packets allowed"))


def main():
    test_file = loader.DATA_PATH / "storage" / "test_content_source.png"
    cached_files = loader.load_user_data("storage_index")
    if not cached_files:
        cached_files = explore_storage()
        loader.store_user_data("storage_index", cached_files)
    cached_tokens = loader.load_user_data("tokens")

    port = serv.get_first_port_from(13131)
    s = ShareServ(port, cached_files, cached_tokens)
    print(port)
    s.mainloop()


if __name__ == '__main__':
    assert loader.get_anchor_dev(Path(".."))
    main()
