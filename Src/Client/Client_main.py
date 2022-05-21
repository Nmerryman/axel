import Services.loader as loader
from Services.data_structures import FileToken
import os

anchor = loader.get_anchor()
# If in a testing environment, use alternative location
if anchor == "DEV":
    from pathlib import Path
    loader.DATA_PATH = Path("dev_data")
    loader.get_anchor()



