# THIS FILE WAS AUTOGENERATED THROUGH file_generator.py

import dataclasses
from dataclasses import dataclass
import json


@dataclass
class FileToken:

    file_name: str
    hash_val: str
    auth_token: str
    valid_until: int

    def __init__(self, file_name=None, hash_val=None, auth_token=None, valid_until=None):
        if not file_name:
            raise ValueError("No parameters given")
        elif isinstance(file_name, dict):
            self._load_dict(file_name)
        elif isinstance(file_name, str) and not hash_val:
            # Assume only json string is passed
            self._load_dict(json.loads(file_name))
        else:
            self.file_name = file_name
            self.hash_val = hash_val
            self.auth_token = auth_token
            self.valid_until = valid_until

    def _load_dict(self, data: dict):
        self.file_name = data["file_name"]
        self.hash_val = data["hash_val"]
        self.auth_token = data["auth_token"]
        self.valid_until = data["valid_until"]

    def _to_dict(self):
        return dataclasses.asdict(self)

    def dumps(self):
        return json.dumps(self._to_dict())


@dataclass
class FileIndex:

    file_name: str
    hash_val: str
    size: int
    lost_access: int

    def __init__(self, file_name=None, hash_val=None, size=None, lost_access=None):
        if not file_name:
            raise ValueError("No parameters given")
        elif isinstance(file_name, dict):
            self._load_dict(file_name)
        elif isinstance(file_name, str) and not hash_val:
            # Assume only json string is passed
            self._load_dict(json.loads(file_name))
        else:
            self.file_name = file_name
            self.hash_val = hash_val
            self.size = size
            self.lost_access = lost_access

    def _load_dict(self, data: dict):
        self.file_name = data["file_name"]
        self.hash_val = data["hash_val"]
        self.size = data["size"]
        self.lost_access = data["lost_access"]

    def _to_dict(self):
        return dataclasses.asdict(self)

    def dumps(self):
        return json.dumps(self._to_dict())


@dataclass
class Gates:

    ip: str
    port: str

    def __init__(self, ip=None, port=None):
        if not ip:
            raise ValueError("No parameters given")
        elif isinstance(ip, dict):
            self._load_dict(ip)
        elif isinstance(ip, str) and not port:
            # Assume only json string is passed
            self._load_dict(json.loads(ip))
        else:
            self.ip = ip
            self.port = port

    def _load_dict(self, data: dict):
        self.ip = data["ip"]
        self.port = data["port"]

    def _to_dict(self):
        return dataclasses.asdict(self)

    def dumps(self):
        return json.dumps(self._to_dict())

