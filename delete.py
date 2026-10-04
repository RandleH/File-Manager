import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument(      "--index"  , required=True    , type=int ,                      help="Episode index to be inserted")
parser.add_argument(      "--logging", default="info"   , type=str ,                      help="Verbose"                     )
parser.add_argument("-i", "--info"   , default=False    ,            action='store_true', help="Print contents"              )
parser.add_argument(      "--soft"   , default=True     ,            action='store_true', help="Query before deleting"       )

(args,unknown_args) = parser.parse_known_args()


def main():
    mgr = FileManager(logging.DEBUG if args.logging=="debug" else logging.INFO)
    mgr.del_index(args.index, query_msg=args.soft)
    if args.info:
        mgr.print_contents()

if __name__ == "__main__":
    main()