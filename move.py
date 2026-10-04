import argparse
import logging
from FileManager import FileManager

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--src"    , required=True, type=int, help="Episode index to be moved")
parser.add_argument("-d", "--dst"    , required=True, type=int, help="Episode expected index"   )
parser.add_argument(      "--logging",                type=str, help="Verbose"                  , default="info")
(args,unknown_args) = parser.parse_known_args()


def main():
    mgr = FileManager(logging.DEBUG if args.logging=="debug" else logging.INFO)
    try:
        index, desc = mgr.inq_index(args.src)
    except TypeError:
        mgr.logger.error(f"Index {args.src} was NOT found in the EP markdown list.")
        exit(1)

    if args.src > args.dst:
        for idx in range(args.src, args.dst, -1):
            mgr.swp_index(idx, idx-1)
    elif args.src < args.dst:
        for idx in range(args.src, args.dst):
            mgr.swp_index(idx, idx+1)
    else:
        mgr.logger.warning("Source Index equals to Destination Index. Skipped.")
        exit(0)
    
    

if __name__ == "__main__":
    main()