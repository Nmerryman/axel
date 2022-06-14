from pathlib import Path
import Src.services.gen_dev_data as gen

"""
This tests dev data generation for mock users and stuff
"""


def test_gen_file_token():
    # Ensure that the functions return something
    assert gen.file_token_default()
    assert gen.file_token_random()
    # make sure it matches up data wise when it matters
    assert gen.file_token_default() == gen.file_token_default()
    assert gen.file_token_default() != gen.file_token_random()
    assert gen.file_token_random() != gen.file_token_random()

