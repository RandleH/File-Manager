import argparse
import logging
import sys
import copy
import re
import os
import stat
import subprocess
from pathlib import Path
try:
    from PrettyLogger import PrettyLogger
except:
    from logger import PrettyLogger


def to_array(inp_str):
    inp_str.replace(' ', "")
    buf = []
    inp_str_trim = re.sub( r'[^\d+:,]', '', inp_str)
    
    for item in re.split(',', inp_str_trim):
        if ':' in item:
            rng = re.split(':', item)
            for x in range(int(rng[0]), int(rng[1])+1):
                buf.append(x)
        else:
            buf.append(int(item))
    return buf

def query(prompt_message="Do you want to proceed?"):
    while True:
        # Get input, strip whitespace, and convert to lowercase
        user_input = input(prompt_message + " (y/n)\n").strip().lower()
        
        # Check for Yes variations
        if user_input in ('y', 'yes', 'Y'):
            return True
            
        # Check for No variations
        if user_input in ('n', 'no', 'N'):
            return False
            
        # Handle invalid inputs
        return None


class Manager:
    def __init__(self, params):
        self.logger = PrettyLogger(self.__class__.__name__, level=logging.DEBUG if params.logging=="debug" else logging.INFO)
        self.path   = Path(os.path.abspath(params.path))
        self.photos = []

        self.user_args     = copy.deepcopy(params)
        self.output_folder = self.user_args.output

        if self.user_args.index_width == 0:
            if self.user_args.device == "sony":
                self.user_args.index_width = 5
            elif self.user_args.device == "fuji":
                self.user_args.index_width = 4

        if self.user_args.output == "":
            self.user_args.output = os.path.join(os.path.abspath(self.user_args.path), "customer")

        self.logger.info("Inisitalizing file manager...")
        
        if self.user_args.device == "unknown":
            self.logger.info("Device not specified. Seaching for the locked photos.")
            
            for item in self.path.iterdir():
                if item.is_file() and Manager.is_finder_locked(item):
                    self.photos.append(item.name)
        else:
            self.user_args.index = to_array(self.user_args.index)
            if self.user_args.device == "sony":
                self.photos = [f"DSC{number:0{self.user_args.index_width}d}.ARW" for number in self.user_args.index]
            elif self.user_args.device == "fuji":
                self.photos = [f"DSCF{number:0{self.user_args.index_width}d}.RAF" for number in self.user_args.index]
            else:
                self.logger.error("Unsupported camera device. Exit with 1.")
                sys.exit(1)

        self.logger.debug(f"\tPhoto to be picked:")
        for cnt, item in enumerate(self.photos):
            self.logger.debug(f"\t[{1+cnt}/{len(self.photos)}] {item}")
        
    
    def is_finder_locked(fp):
        # Ensure the file exists first
        if not os.path.exists(fp):
            return False
            
        # The st_flags attribute is unique to BSD-based systems like macOS
        try:
            file_info = os.stat(fp)
            if hasattr(file_info, 'st_flags'):
                # Perform a bitwise AND check against the user immutable flag
                return bool(file_info.st_flags & stat.UF_IMMUTABLE)
        except OSError:
            pass
            
        return False
    
    def unlock(self):
        for item in self.path.iterdir():
            if item.is_file() and Manager.is_finder_locked(item):
                if self.user_args.query and False==query(f"Unlock {item}?"):
                    continue
                file_info = os.stat(item)
                new_flags = file_info.st_flags & ~stat.UF_IMMUTABLE
                os.chflags(os.path.join(self.path.as_posix(), item.name), new_flags)
        

    def fetch(self, open_when_finshed=True):
        try:
            self.logger.debug(f"\tcreate the output folder: {self.output_folder}")
            subprocess.run(['mkdir', '-p', self.output_folder], check=True)
        except Exception as e:
            self.logger.error(f"failed to create the folder {self.output_folder}. Signature:\n\t{e}")
            return 1

        cnt = 0
        for item in self.photos:
            try:
                if self.user_args.no_copy:
                    self.logger.debug(f"\tmoving {item}...")
                    operator = 'mv'
                    if self.user_args.query and False==query(f"Move {item} to {self.output_folder}?"):
                        continue
                else:
                    self.logger.debug(f"\tcopying {item}...")
                    operator = 'cp'
                subprocess.run([operator, os.path.join(self.path.as_posix(), item), self.output_folder], check=True)
                self.logger.debug(f"\tdone")
                cnt += 1
            except Exception as e:
                self.logger.warning(f"Failed. Signature:{e}")

            self.logger.debug("moving {}...")
        
        self.logger.info(f"Completed. Sucessfully copied {cnt} photos to {self.output_folder}.")

        if self.user_args.unlock == True:
            self.unlock()

        if open_when_finshed == True:
            subprocess.run(['open', self.output_folder], check=False)
        
        return 0



# NOTE: python3 ${DIR}/customer.py --device sony --index [3209,3740:3742,3749] --path '/Volumes/Untitled/DCIM/judy_毕业照'
# NOTE: python3 ${DIR}/customer.py --path '/Volumes/Untitled/DCIM/judy_毕业照'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i"     , "--index"             , action="store"     , required=False                 ,           help="Photo index list. Eg: [1,2,3] [1:3]")
    parser.add_argument(           "--logging"           , action="store"     ,                 default="info", type=str, help="Verbose Level: info / debug")
    parser.add_argument("-d"     , "--device"            , action="store"     ,                 default="unknown", type=str, help="Camera device: sony / fuji")
    parser.add_argument("-p"     , "--path"              , action="store"     , required=True                 , type=str, help="Photo path to be searched")
    parser.add_argument("-o"     , "--output"            , action="store"     ,                 default=""    , type=str, help="Output folder")
    parser.add_argument(           "--index_width"       , action="store"     , required=False, default=0     , type=int, help="Index digit width in the name. Eg: The width of DSC0999 is 4.")
    parser.add_argument("-nocopy", "--nocopy"            , action="store_true",                 default=False ,           help="Moving photos instead of copying")
    parser.add_argument("-unlock", "--unlock"            , action="store_true", required=False, default=False ,           help="Remove locked flag when finished.")
    parser.add_argument(           "--silent"            , action="store_true",                 default=False ,           help="Do not open the folder when finished")
    parser.add_argument("-q"     , "--query"             , action="store_true",                 default=False ,           help="Query operation mode. When there is I/O operation, query user to proceed.")
    parser.add_argument("-f"     , "--force"             , action="store_true",                 default=False ,           help="Force operation mode. Execute the operation immediately.")
    parser.add_argument("-v"     , "--version"           , action="version"   , version='%(prog)s 1.0.0')
    (args,unknown_args) = parser.parse_known_args()

    
    mgr = Manager(args)
    mgr.fetch(open_when_finshed=(args.silent==False))

