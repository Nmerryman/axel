import json
import enum
import socket
from string import ascii_letters
from typing import Union

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


class ConnectionClosed(Exception):
    pass


class WrappedConnection:

    def __init__(self, connection: socket.socket):
        self.conn = connection
        if self.conn:  # This is for when I want to pass None for debugging
            self.conn.setblocking(False)
        self.partial = b''
        self.finished = []
        self.recv_size = 1000
        # Packet mode takes advantage of json formatting to detect start and ends of packets and then rebuilds the original messages
        # Stream mode is more dynamic
        #     First byte is message mode (0=stream, 1=packet, 2=meta packet)
        #     Second byte dictates how many bytes are needed to represent the message
        #     Next n bytes is the exact length of the message
        #     Finally the message gets sent
        #       In theory this system can send up to 18 exabytes of data per message
        self.alive = True

    @staticmethod
    def life_check(func):
        def wrapper(self):
            if not self.alive:
                raise ConnectionClosed("Socket has been closed and should not receive anything else")
            func(self)
        return wrapper

    @life_check
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

    @life_check
    def conn_status(self):
        a, b, c = select.select([self.conn], [self.conn], [self.conn])
        options = set()
        if a:
            options.add("read")
        if b:
            options.add("write")
        if c:
            options.add("error")
        return options

    def parse_message(self):
        """
        Extract only the first message from the partial
        """
        if self.partial:
            if self.partial[0] == 1:  # if it's a packet
                depth = 1
                index = 2  # skip the first "{"
                max_len = len(self.partial)
                while depth > 0:
                    if index > max_len:
                        print("emergency return, should probably do something here")  # TODO
                        return False
                    match self.partial[index]:
                        case 123:  # TODO see if there is a way to evaluate these instead of hardcoding
                            depth += 1
                        case 125:
                            depth -= 1
                        case _:
                            pass
                    index += 1
                # We already checked for a valid finished message
                cropped = self.partial[1:index]
                self.partial = self.partial[index:]
                self.finished.append(Packet().parse(cropped))
            elif self.partial[0] == 0:
                partial_len = len(self.partial)
                if partial_len < 2:  # All of these checks are to ensure loaded message is large enough, TODO wrap all in a try?
                    return False
                root_len = self.partial[1]
                if partial_len < root_len + 2:
                    return False
                msg_len = int.from_bytes(self.partial[2:2 + root_len], 'little')
                if partial_len < msg_len + root_len + 2:
                    return False

                # We should have verified the length by now
                self.finished.append(self.partial[2+root_len:2+root_len+msg_len])
                self.partial = self.partial[2+root_len+msg_len:]

            elif self.partial[0] == 2:
                # This is for meta commands
                depth = 1
                index = 2  # skip the first "{"
                max_len = len(self.partial)
                while depth > 0:
                    if index > max_len:
                        print("emergency return, should probably do something here")  # TODO
                        return False
                    match self.partial[index]:
                        case 123:  # TODO see if there is a way to evaluate these instead of hardcoding
                            depth += 1
                        case 125:
                            depth -= 1
                        case _:
                            pass
                    index += 1
                # We already checked for a valid finished message
                cropped = self.partial[1:index]
                self.partial = self.partial[index:]

                msg = Packet().parse(cropped)
                if not msg.type == 'meta':  # We only want meta commands when going down this path
                    return False
                if msg.value == 'close':
                    self.alive = False
        return True

    def parse_partial(self):
        """
        This would try to parse the entire partial instead of extracting one at a time.
        """
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
                    self.finished.append(Packet().parse(self.partial[s:e+1]))  # TODO the order of these may be reversed
                self.partial = self.partial[ends[-1]+1:]
        elif self.mode == "stream":
            current = len(self.partial)
            if current > 0:
                root_len = self.partial[0]
                if current > root_len + 1:
                    msg_len = int.from_bytes(self.partial[1:root_len + 1], 'little')
                    if current >= msg_len + root_len + 1:
                        self.finished.append(self.partial[1 + root_len:1 + root_len + msg_len])
                        self.partial = self.partial[1+root_len+msg_len:]
                        self.parse_partial()  # Each iteration can only load 1 message at a time

    @life_check
    def send_obj(self, data: Union[bytes, Packet]):
        prep: bytes = b''
        if isinstance(data, bytes):
            prep = b'\x00' + self.prep_stream(data)
        elif isinstance(data, Packet):
            if not data.type == 'socket meta':
                prep = b'\x01' + data.generate()
            else:
                prep = b'\x02' + data.generate()
        self.conn.sendall(prep)
        print(prep)

    @life_check
    def close(self):
        packet = Packet("socket meta", 'close')
        self.send_obj(packet)

    @staticmethod
    def prep_stream(data: bytes):
        size_len = len(data)
        size_byte = size_len.to_bytes((size_len.bit_length() + 7) // 8, 'little')
        root_len = len(size_byte)
        root_byte = root_len.to_bytes(1, 'little')
        log("Generated byte stream", size_len, size_byte, root_len, root_byte)
        return root_byte + size_byte + data




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
