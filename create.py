import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument(      "--index"  , required=True    , type=int ,                      help="Episode index to be inserted")
parser.add_argument("-t", "--title"  , default='Untitle', type=str ,                      help="Episode title (optional)"    )
parser.add_argument(      "--logging", default="info"   , type=str ,                      help="Verbose"                     )
parser.add_argument("-i", "--info"   , default=False    ,            action='store_true', help="Print contents"              )


(args,unknown_args) = parser.parse_known_args()


def main():
    mgr = FileManager(logging.DEBUG if args.logging=="debug" else logging.INFO)
    mgr.new_index(args.index, title=args.title)
    if args.info:
        mgr.print_contents()

if __name__ == "__main__":
    main()