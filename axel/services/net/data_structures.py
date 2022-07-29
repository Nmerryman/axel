import json
import enum


DEBUG = True


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
