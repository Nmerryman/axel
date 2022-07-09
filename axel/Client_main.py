import services.loader as loader
from services.data_structures import FileToken
from services.gen_dev_data import *
import os
import argparse


anchor = loader.get_anchor()
# If in a testing environment, use alternative location
if anchor == "DEV":
    from pathlib import Path
    loader.DATA_PATH = Path("dev_data")
    loader.get_anchor()


def main():

    loader.store_user_data("tokens", [file_token_default()])
    l = loader.load_user_data("tokens")
    t = file_token_default()
    t.file_name = "e"
    print(t == l[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true", help="Use client as an entry point")
    parser.add_argument("--director", action="store_true", help="Act as a central point that assigns queues")
    parser.add_argument("--root", action="store_true", help="Use only with director flag. Treats as client as root")

    args = parser.parse_args()
    if args.gate:
        print("Acting as gate")
    else:
        print("Not a gate")
    main()

