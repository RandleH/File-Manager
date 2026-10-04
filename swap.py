import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument( '-i', '--index', type=int, nargs=2, required=True, help='Episode index to be swapped. This must be in pair.')
parser.add_argument(      "--logging", type=str                 , default="info", help="Verbose"                    )
(args,unknown_args) = parser.parse_known_args()


def main():
    mgr = FileManager(logging.DEBUG if args.logging=="debug" else logging.INFO)
    mgr.swp_index(args.index[0], args.index[1])
    

if __name__ == "__main__":
    main()