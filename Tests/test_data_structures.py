from pathlib import Path
import json
import axel.services.data_structures as ds


def test_FileToken():
    # Basic generation
    t = ds.FileToken('a', 'b', 'c', 1)
    assert isinstance(t, ds.FileToken)
    assert t.file_name == 'a'
    assert t.hash_val == 'b'
    assert t.auth_token == 'c'
    assert t.valid_until == 1

    # dumping and loading from string works correctly
    d = t.dumps()
    n = ds.FileToken(d)
    assert t == n

    # Can it parse a dictionary too?
    n = ds.FileToken(t._to_dict())
    assert t == n




