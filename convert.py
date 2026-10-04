import os
import subprocess
from pathlib import Path
from multiprocessing import Pool
import glob
import argparse
from logger import PrettyLogger
import logging

logger = PrettyLogger(__name__, level=logging.DEBUG)

def make_command(args):
    '''
    for f in *.mp4; do
        ffmpeg -i "$f" -c:v copy -c:a aac -ac 2 -b:a 192k "${f%.mp4}.tmp.mp4" && mv "${f%.mp4}.tmp.mp4" "$f"
    done
    '''
    logger.info(f"Search the directory: {args.dir}\n")
    cmd = []
    files_all  = set(glob.glob(os.path.join(args.dir, "**",      "*.{}".format(args.fmt)), recursive=True))
    files_done = set(glob.glob(os.path.join(args.dir, "**", "benz_*.{}".format(args.fmt)), recursive=True))
    files_todo = files_all - files_done

    logger.debug("Found the following media files:")
    for item in files_all:
        logger.debug(f"\t* {item}")

    logger.debug("Skip the following media files:")
    for item in files_done:
        logger.debug(f"\t* {item}")
    
    logger.debug("Media files to be converted:")
    for item in files_todo:
        logger.debug(f"\t* {item}")

    logger.info("\n")
    logger.info("Commands to be loaded:")
    for file in files_todo:
        item = Path(file)

        file_tmp  = os.path.join(item.parent, item.stem + "_tmp" + ".mp4")  # insert .tmp in the middle
        file_benz = os.path.join(item.parent, "benz_" + item.stem + ".mp4") # add benz prefix

        if item.suffix == ".mp4":
            misc_cfg = r"-c:v copy"
        elif item.suffix == ".rmvb":
            misc_cfg = r"-c:v libx264 -preset medium -crf 23"
        else:
            misc_cfg = r"-c:v copy"


        cmd.append(
            # ffmpeg -i input.mp4  -map 0:v:0 -map 0:a:0 -c:v copy                           -c:a aac -ac 2 -b:a 192k -movflags +faststart output.mp4
            # ffmpeg -i input.rmvb -map 0:v:0 -map 0:a:0 -c:v libx264 -preset medium -crf 23 -c:a aac -ac 2 -b:a 192k -movflags +faststart output.mp4
            "ffmpeg -i {} -map 0:v:0 -map 0:a:0 {} -c:a aac -ac 2 -b:a 192k -movflags +faststart {} && mv {} {} && mv {} {}".format(
                file,
                misc_cfg,
                file_tmp,
                file_tmp,
                file,
                file,
                file_benz
            )
        )
        logger.debug(f"\t$ {cmd[-1]}")

    logger.info(f"Searching completed\n")
    return cmd



def run_command(command):
    """Function to execute a single shell command."""
    try:
        # subprocess.run is the recommended way to execute shell commands
        # check=True raises an error if the command fails
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, errors="replace")
        return f"SUCCESS: {command}\nOutput: {result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        return f"FAILED: {command}\nError: {e.stderr.strip()}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--dir"         , required=True                              , help="Folder location")
    parser.add_argument(      "--fmt"         , required=True                              , help="Video format to search: [ mp4 | rmvb ]")
    parser.add_argument(      "--logging"     , required=False, default="info"   , type=str, help="Verbose Level: [ debug | info ]")
    parser.add_argument(      "--mp"          , required=False, default=6        , type=int, help="Multiprocess")
    (args,unknown_args) = parser.parse_known_args()

    commands = make_command(args)
    # Create a pool of workers (defaults to number of CPU cores)
    with Pool(processes=args.mp) as pool:
        # Map the commands to the worker function
        results = pool.map(run_command, commands)

    for res in results:
        logger.info(res)