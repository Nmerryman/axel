import sys
from pathlib import Path

"""
This relies on absolute paths to find the correct imports and could break at any time
"""


def import_file(path: Path):
    abs_loc = (Path(sys.path[0]) / ".." / "Src" / "Client" / "Services").resolve()
    name = path.stem
    sys.path.insert(1, abs_loc.__str__())
    return __import__(name.__str__())
