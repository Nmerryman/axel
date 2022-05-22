from import_wanted import import_file
from pathlib import Path

gen = import_file(Path("gen_dev_data.py"))


def test_gen_file_token():
    # Ensure that the functions return something
    assert gen.file_token_default()
    assert gen.file_token_random()
    # make sure it matches up data wise when it matters
    assert gen.file_token_default() == gen.file_token_default()
    assert gen.file_token_default() != gen.file_token_random()
    assert gen.file_token_random() != gen.file_token_random()

