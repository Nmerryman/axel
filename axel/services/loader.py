import os
from typing import Union
from pathlib import Path
from .data_structures import *
import json


"""
This indexes and loads/stores user info
It also generates any missing files for first setup
"""

DATA_PATH = Path("data")  # Where all user data is stored
anchor = "anchor.txt"  # Name of anchor file


def get_anchor():
    """
    This is more to test that loader can find the right directory
    It will check what mode to run in based on text in anchor.txt and generate any missing files/directories.
    All other code assumes all needed files already exist.
    :return: Anchor text
    """

    DATA_PATH.mkdir(exist_ok=True)  # Data folder exists

    # Anchor file exists and get text
    if not (DATA_PATH / anchor).exists():
        with open(DATA_PATH / anchor, 'w') as f:
            f.write("GENERATED")
            text = "GENERATED"
    else:
        with open(DATA_PATH / anchor, "r") as f:
            text = f.read()

    # make sure all needed files are here
    (DATA_PATH / "storage").mkdir(exist_ok=True)
    (DATA_PATH / "user").mkdir(exist_ok=True)
    # It may be worth putting this data into a database
    (DATA_PATH / "user" / "tokens").touch(exist_ok=True)
    (DATA_PATH / "user" / "gates").touch(exist_ok=True)
    (DATA_PATH / "user" / "storage_index").touch(exist_ok=True)
    (DATA_PATH / "user" / "directors").touch(exist_ok=True)
    (DATA_PATH / "user" / "logs").touch(exist_ok=True)

    return text


def get_anchor_dev(mod: Path = None):
    global DATA_PATH
    if mod:
        DATA_PATH = mod / Path("dev_data")
        DATA_PATH.resolve()
    else:
        DATA_PATH = Path("dev_data")
    return get_anchor()


# may not even want these helpers because they do so little
def store_user_str(string: str, location: Union[str, Path]):
    (DATA_PATH / "user" / location).write_text(string)


def load_user_str(location: Union[str, Path]) -> str:
    text = (DATA_PATH / "user" / location).read_text()
    if text == "":
        text = "[]"
    return text


def store_user_data(name: str, data: list[FileToken | FileIndex | Client | LogEntry]): # the actual type doesn't matter because they all have a dump method
    if name in ("tokens", "gates", "directors", "logs", "storage_index"):

        prep = [a.dumps() for a in data]
        store_user_str(json.dumps(prep), name)
    else:
        raise ValueError(f"{name} is not a valid datafile name")


def load_user_data(name: str) -> list[FileToken | FileIndex | Client | LogEntry]:  # same type comment as before
    if name in ("tokens", "gates", "directors", "logs", "storage_index"):
        name_to_class = {"tokens": FileToken, "gates": Client, "directors": Client, "logs": LogEntry, "storage_index": FileIndex}
        data = json.loads(load_user_str(name))
        return [name_to_class[name](a) for a in data]
    else:
        raise ValueError(f"{name} is not a valid datafile name")


