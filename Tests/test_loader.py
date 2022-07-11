import axel.services.loader as loader
import axel.services.data_structures as ds
from pathlib import Path
import os
import random


def test_anchor():
    loader.DATA_PATH = Path("axel/dev_data")
    assert loader.get_anchor()
    assert os.path.exists("axel/dev_data")
    assert os.path.exists("axel/dev_data/storage")
    assert os.path.exists("axel/dev_data/user/logs")


def test_store_and_read_str():
    test_str = str(random.randint(0, 99999999))
    loader.store_user_str(test_str, "gates")
    text = loader.load_user_str("gates")
    assert text == test_str


def test_store_and_read_data():
    test_str = str(random.randint(0, 99999999))
    test_gate = ds.Client(test_str, 1)
    loader.store_user_data("gates", [test_gate])
    loaded = loader.load_user_data("gates")
    assert loaded
    assert loaded[0]
    assert loaded[0].ip == test_str
    assert loaded[0].ip != "aaa"


def test_overwrite():
    start_text = "a"*200
    loader.store_user_str(start_text, "gates")
    loader.store_user_str("bbb", "gates")
    read = loader.load_user_str("gates")
    assert read == "bbb"

