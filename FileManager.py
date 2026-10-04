from logger import PrettyLogger
import logging
import os
import re

def query(msg):
    ans = input(f"{msg} [Y/N]? ")
    if ans=="Y":
        return True
    else:
        return False


class Exec:
    def __init__(self, level):
        self.logger = PrettyLogger(self.__class__.__name__, level=level)
    
    def run(self, cmd):
        self.logger.debug(f"\texecuting command line: {cmd}")
        os.system(cmd)


class FileManager:
    def __init__(self, level=logging.INFO):
        self.logger   = PrettyLogger(self.__class__.__name__, level=level)
        self.location = os.path.dirname(os.path.abspath(__file__))
        self.exec     = Exec(level)
    
    def __make_filename__(self, index:int, title=None, sp=" "):
        return "EP{}{}-{}{}.md".format(str(index), sp, sp, "" if title == None else str(title))
    
    def __make_title__(self, index:int, title=None):
        filename = self.__make_filename__(index, title=title)
        # Example of overwriting the first line
        with open(filename, 'r') as file:
            lines = file.readlines()

        # Replace the first line (index 0)
        title_str = f"# <span style=\"font-family: Zapfino;\">Episode {index:02d} {title}</span>\n"
        try:
            lines[0] = title_str
        except IndexError: # Empty file
            lines = [title_str]

        # Write back to the same file
        with open(filename, 'w') as file:
            file.writelines(lines)

    def rnm_index(self, old_index:int, new_index:int):
        """
        Rename an indexed item
        Title will inherit from the old one.
        """
        self.logger.debug(f"\trename file: [EP{new_index} - *.md] => [EP{old_index} - *.md] ")

        pattern = "^(EP{}) - (.*).md".format(old_index)

        old_file_name = None
        new_file_name = None
        title         = None
        for filename in os.listdir(self.location):
            filepath = os.path.join(self.location, filename)
            if os.path.isfile(filepath):
                res = re.match(pattern, filename)
                if res:
                    title          = res.group(2)
                    old_file_name = filename
                    new_file_name = f"EP{new_index} - {title}.md"
                    break

        if old_file_name == None or new_file_name == None:
            self.logger.warning(f"There is no files starting with EP{old_index}")
            return

        try:
            # Rename the file
            os.rename(old_file_name, new_file_name)
            self.logger.info(f"File '{old_file_name}' successfully renamed to '{new_file_name}'.")
        except FileNotFoundError:
            self.logger.warning(f"Error: The file '{old_file_name}' was not found.")
        except OSError as e:
            self.logger.warning(f"Error renaming file: {e}")
        
        self.__make_title__(new_index, title)

    def inq_index(self, index:int):
        """
        Inquery an intexed item. (This function will NOT involve any file operation.)
        
        Return index and title if found.
        Return `None` if NOT found.
        """
        pattern = "^(EP{}) - (.*).md".format(index)
        compiled_pattern = re.compile(pattern)
        for filename in os.listdir(self.location):
            filepath = os.path.join(self.location, filename)
            res      = compiled_pattern.match(filename)
            if os.path.isfile(filepath) and res:
                title = res.group(2)
                self.logger.debug(f"\tfound an existing {index=} {title=}")
                return index, title
        return None
    
    def inc_index(self, index:int):
        """
        Increase the indexed item by 1. 
        This may be recursive until gap or end of the list were reached.
        """
        if self.inq_index(index):
            self.inc_index(index+1)
            self.rnm_index(index, index+1)

    def dec_index(self, index:int):
        """
        Increase the indexed item by 1. 
        This may be recursive until gap or end of the list were reached.
        """
        if index == 1:
            self.warning("Can NOT decrease the index from begining. EP0 will be overwritten.")
            return
        if self.inq_index(index):
            self.rnm_index(index, index-1)
            self.dec_index(index+1)

    def new_index(self, index:int, title=None):
        """
        Create an new indexed item.
        """
        filename = self.__make_filename__(index, title, sp="\ ")
        if self.inq_index(index):
            self.inc_index(index)
        
        filepath = os.path.join(self.location, filename)
        self.exec.run(f"touch {filepath}")
        self.__make_title__(index, title)

    def swp_index(self, index1:int, index2:int):
        """
        Swap 2 indexed items. Titles remain the same.
        """
        try:
            index1, title1 = self.inq_index(index1)
            File1 = self.__make_filename__(index1, title=title1)
            
        except TypeError:
            self.logger.warning(f"Index {index1} was NOT found in the EP markdown list.")
            File1 = None
            
        try:
            index2, title2 = self.inq_index(index2)
            File2 = self.__make_filename__(index2, title=title2)
        except TypeError:
            self.logger.warning(f"Index {index2} was NOT found in the EP markdown list.")
            File2 = None

        if File1 == None and File2 == None:
            self.logger.warning("Both files are missing in the EP list. Skipped.")
        elif File1 == None and File2 != None:
            self.logger.warning(f"Since Index {index1} was missing. Rename {index2} to {index1} only")
            os.rename(File2, self.__make_filename__(index1, title=title2))
            self.__make_title__(index1, title2)
        elif File1 != None and File2 == None:
            self.logger.warning(f"Since Index {index2} was missing. Rename {index1} to {index2} only")
            os.rename(File1, self.__make_filename__(index2, title=title1))
            self.__make_title__(index2, title1)
        else:
            if title1 != title2:
                os.rename(File2, self.__make_filename__(index1, title=title2)) 
                os.rename(File1, self.__make_filename__(index2, title=title1))
            else:
                os.rename(File2                  , f"EPTEMP - {title2}.md")
                os.rename(File1                  , self.__make_filename__(index2, title=title1))
                os.rename(f"EPTEMP - {title2}.md", self.__make_filename__(index1, title=title2))
            
            temp   = index1
            index1 = index2
            index2 = temp

            self.__make_title__(index1, title1)
            self.__make_title__(index2, title2)

    def del_index(self, index:int, query_msg=True):
        """
        Delete an indexed item.
        """
        try:
            index, title = self.inq_index(index)
        except TypeError:
            self.logger.error(f"Index {index} was NOT found in the EP markdown list.")
        
        filename = self.__make_filename__(index, title=title, sp="\ ")
        if (query_msg == True and True == query(f"Are you sure to delete this episode? {filename}")) or query_msg == False:
            self.exec.run(f"rm {filename}")
        self.dec_index(index+1)
        
    def print_contents(self):
        print("="*64)
        print("CONTENTS")
        print("="*64)

        for idx in range(0,100):
            try:
                index, title = self.inq_index(idx)
                fname = self.__make_filename__(index, title=title)
                print(f"[EP{index} - {title}](./{fname})")
            except TypeError:
                continue
        
