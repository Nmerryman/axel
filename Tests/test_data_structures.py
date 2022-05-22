from pathlib import Path
# import import_wanted
import json
import Src.services.data_structures as ds

# ds = import_wanted.import_file(Path("data_structures.py"))


def test_FileToken():
    # Basic generation
    t = ds.FileToken('a', 'b', 'c', 1)
    assert isinstance(t, ds.FileToken)
    assert t.file_name == 'a'
    assert t.hash_val == 'b'
    assert t.auth_val == 'c'
    assert t.valid_until == 1

    # dumping and loading from string works correctly
    d = t.dumps()
    n = ds.FileToken(d)
    assert t == n

    # Can it parse a dictionary too?
    n = ds.FileToken(t._to_dict())
    assert t == n




