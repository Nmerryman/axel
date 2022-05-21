import os
from pathlib import Path


"""
This indexes and loads user info
"""

DATA_PATH = Path("Data")


def get_anchor():
    """
    This is more to test that loader can find the right directory
    :return: Anchor text
    """
    with open(DATA_PATH / "anchor.txt", "r") as f:
        text = f.read()
    return text
