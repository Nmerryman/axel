import os
from pathlib import Path


"""
This indexes and loads user info
"""

DATA_PATH = Path("data")  # Where all user data is stored
anchor = "anchor.txt"  # Name of anchor file


def get_anchor():
    """
    This is more to test that loader can find the right directory
    It will check what mode to run in based on text in anchor.txt and generate any missing files/directories.
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
