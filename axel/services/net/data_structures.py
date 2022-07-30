import json
import enum
import socket
from string import ascii_letters
import select

DEBUG = False


def log(*text):
    if DEBUG:
        print("D:", *text)


# We are assuming entire packet fits in recv size. May need to add proper data buffering/loading otherwise
# It is not super optimised for readability
class Packet:

    def __init__(self, data_type=None, value=None, data=None, extra=None):
        if not data_type:
            data_type = ''
        if not value:
            value = ''
        if not data:
            data = ''
        if not extra:
            extra = ''
        self.storage = {"TYPE": data_type, "VALUE": value, "DATA": data, "EXTRA": extra}
        self.type = data_type
        self.value = value
        self.data = data
        self.extra = extra

    def __getitem__(self, name: str):
        return self.storage[name.upper()]

    def __eq__(self, other):
        return self.storage == other.storage

    def load_storage(self):
        self.type = self.storage["TYPE"]
        self.value = self.storage["VALUE"]
        self.data = self.storage["DATA"]
        self.extra = self.storage["EXTRA"]

    def set_value(self, value):
        self.value = value
        self.storage["VALUE"] = value

    def set_type(self, data_type):
        self.type = data_type
        self.storage["TYPE"] = data_type

    def set_data(self, data):
        self.data = data
        self.storage["DATA"] = data

    def set_extra(self, extra):
        self.extra = extra
        self.storage["EXTRA"] = extra

    def generate(self):
        return json.dumps(self.storage).encode()

    def parse(self, data):
        check = str(data, "utf-8")
        if check == "":
            self.storage = Packet().storage  # use empty default
        else:
            self.storage = json.loads(check)

        self.load_storage()
        log(str(data, "utf-8"))
        return self


class WrappedConnection:

    def __init__(self, connection: socket.socket):
        self.conn = connection
        if self.conn:  # This is for when I want to pass None for debugging
            self.conn.setblocking(False)
        self.partial = b''
        self.finished = []
        self.recv_size = 1000
        self.mode = "packet"
        # Packet mode takes advantage of json formatting to detect start and ends of packets and then rebuilds the original messages
        # Stream mode is more dynamic
        #     First byte dictates how many bytes are needed to represent the message
        #     Next n bytes is the exact length of the message
        #     Finally the message gets sent
        #       In theory this system can send up to 18 exabytes of data per message
        self.alive = True

    def load_awaited(self):
        data = ""
        first = True
        readable = []
        while (first or readable) and self.alive:
            readable, _, errors = select.select([self.conn], [], [self.conn], 0)
            if readable:
                self.partial += self.conn.recv(self.recv_size)
                readable = []
            first = False

    def parse_partial(self):
        if self.mode == "packet":
            depth = 0
            starts = []
            ends = []
            for num_a, a in enumerate(self.partial):
                if a == ord(b'{'):
                    if depth == 0:
                        starts.append(num_a)
                    depth += 1
                if a == ord(b'}'):
                    depth -= 1
                    if depth == 0:
                        ends.append(num_a)
            if len(starts) > len(ends):
                starts.pop()
            if len(starts) == len(ends) and len(ends) > 0:  # We may be able to optomize this, but it's probably not needed
                for s, e in zip(starts, ends):
                    self.finished.append(Packet().parse(self.partial[s:e+1]))
                self.partial = self.partial[ends[-1]+1:]

    def load_next(self):
        found = False
        data = ""
        while not found or data:
            data = self.conn.recv(self.recv_size)
            if data:
                found = True


class MessageType(enum.IntEnum):
    command = enum.auto()
    text = enum.auto()
    empty = enum.auto()


class Commands(enum.IntEnum):
    greet = enum.auto()
    close = enum.auto()
    exit = enum.auto()
    is_alive = enum.auto()
    request = enum.auto()
    broadcast = enum.auto()
    unblock = enum.auto()
