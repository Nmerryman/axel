import os
from pathlib import Path
import json


"""
This indexes and loads/stores user info
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
    (DATA_PATH / "user" / "tokens").touch(exist_ok=True)
    (DATA_PATH / "user" / "gates").touch(exist_ok=True)

    return text


# may not even want these helpers because they do so little
def store_user_str(string, location):
    (DATA_PATH / "user" / location).write_text(string)


def load_user_str(string, location):
    (DATA_PATH / "user" / location).read_text(string)




