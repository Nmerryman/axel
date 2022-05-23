import dataclasses
from dataclasses import dataclass
import json


def gen_class(name: str, fields: dict = None):
    # Generate the new class as a string to execute
    if not fields or len(fields) < 2:
        raise ValueError("fields must be defined with at least 2 pairs")

    # Class name
    cls = f"""
@dataclass
class {name}:\n
"""
    # class fields
    for k, v in fields.items():
        cls += f"    {k}: {v.__name__}\n"

    # prep names
    init_vars = "=None, ".join(fields.keys())
    cls += f"    def __init__(self, {init_vars}=None):\n"
    # rest of init
    cls += f"""        if not data_or_name:
            raise ValueError("No parameters given")
        elif isinstance(data_or_name, dict):
            self._load_dict(data_or_name)
        elif isinstance(data_or_name, str) and not {list(fields.keys())[1]}:
            # Assume only json string is passed
            self._load_dict(json.loads(data_or_name))
        else:\n""".replace("data_or_name", list(fields.keys())[0])  # prob need new line
    # init else section
    for a in fields.keys():
        cls += f"            self.{a} = {a}\n"
    # add load_dict
    cls += "    def _load_dict(self, data: dict):\n"
    for a in fields.keys():
        cls += f'        self.{a} = data["{a}"]\n'
    # final methods
    cls += """    def _to_dict(self):
        return dataclasses.asdict(self)

    def dumps(self):
        return json.dumps(self._to_dict())"""

    # ast_cls = ast.parse(cls, filename="", mode="exec")
    exec(compile(cls, "", "exec"))
    exec(f"globals()['{name}'] = locals()['{name}']")
    # exec(f"{name} = {locals()[name]}")
    # exec(f"{name} = 1")
    # print(globals())


gen_class("FileToken", {"file_name": str, "hash_val": str, "auth_val": str, "valid_until": int})


# KEEP OLD VERSION IN-CASE THIS WAS A MISTAKE
# @dataclass
# class FileToken:
#     """
#     These tokens are sent to client as single use verification keys to permit sharing individual files to external connections
#     """
#     file_name: str  # not sure if we want to make the server worry about this
#     hash_val: str
#     auth_val: str
#     valid_until: int
#
#     def __init__(self, data_or_name=None, hash_val=None, auth_val=None, valid_until=None):
#         # This should parse everything I throw at it
#         if not data_or_name:
#             raise ValueError("No parameters given")
#         elif isinstance(data_or_name, dict):
#             self._load_dict(data_or_name)
#         elif isinstance(data_or_name, str) and not hash_val:
#             # Assume only json string is passed
#             self._load_dict(json.loads(data_or_name))
#         else:
#             self.file_name = data_or_name
#             self.hash_val = hash_val
#             self.auth_val = auth_val
#             self.valid_until = valid_until
#
#     def _load_dict(self, data: dict):
#         self.file_name = data["file_name"]
#         self.hash_val = data["hash_val"]
#         self.auth_val = data["auth_val"]
#         self.valid_until = data["valid_until"]
#
#     def _to_dict(self):
#         return dataclasses.asdict(self)
#
#     # get string/json interpretation
#     def dumps(self):
#         return json.dumps(self._to_dict())


# gen_class("Thing", {"name": str, "file": str})
# print(Thing)
# t = Thing("a", "b")
# print(t)
# print(t.name)
#
# print("Thing" in globals())
# print(globals())
