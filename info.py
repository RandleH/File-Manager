import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument("--logging", type=str, default="info", help="Verbose")
(args,unknown_args) = parser.parse_known_args()


def main():
    mgr = FileManager(logging.DEBUG if args.logging=="debug" else logging.INFO)
    mgr.print_contents()


if __name__ == "__main__":
    main()