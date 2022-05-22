import services.loader as loader
from services.data_structures import FileToken
from services.gen_dev_data import *
import os

anchor = loader.get_anchor()
# If in a testing environment, use alternative location
if anchor == "DEV":
    from pathlib import Path
    loader.DATA_PATH = Path("dev_data")
    loader.get_anchor()

loader.store_file_tokens([file_token_default()])
l = loader.load_file_tokens()
t = file_token_default()
t.file_name = "e"
print(t == l[0])

