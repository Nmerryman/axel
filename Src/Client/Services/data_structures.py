import dataclasses
from dataclasses import dataclass
import json


@dataclass
class FileToken:
    file_name: str  # not sure if we want to make the server worry about this
    hash_val: str
    auth_val: str
    valid_until: int

    def __init__(self, data_or_name=None, hash_val=None, auth_val=None, valid_until=None):
        # This should parse everything I throw at it
        if not data_or_name:
            raise ValueError("No parameters given")
        elif isinstance(data_or_name, dict):
            self._load_dict(data_or_name)
        elif isinstance(data_or_name, str) and not hash_val:
            # Assume only json string is passed
            self._load_dict(json.loads(data_or_name))
        else:
            self.file_name = data_or_name
            self.hash_val = hash_val
            self.auth_val = auth_val
            self.valid_until = valid_until
    
    def _load_dict(self, data: dict):
        self.file_name = data["file_name"]
        self.hash_val = data["hash_val"]
        self.auth_val = data["auth_val"]
        self.valid_until = data["valid_until"]

    def _to_dict(self):
        return dataclasses.asdict(self)

    # get string/json interpretation
    def dumps(self):
        return json.dumps(self._to_dict())