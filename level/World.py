import json, os

from .Level import Level


# Keeps list of level data and tracks current level
class World:
    # Takes file path of root level data file (i.e. ldtk file)
    def __init__(self, path):
        self.levels = list()
        self.__lvl_i = -1
        self.parse_json(path)

    # Reads each of the level data files (produced from the LDtk editor)
    # Stores levels in list
    def parse_json(self, path):
        dirpath = os.path.dirname(path)
        with open(path, "r") as fp:
            data = json.load(fp)
            for lvl_data in data["levels"]:
                lvl_relpath = lvl_data["externalRelPath"]
                lvl_abspath = os.path.join(dirpath, lvl_relpath)
                self.levels.append(Level(lvl_abspath))
    
    @property
    def first_level(self):
        self.__lvl_i = 0
        return self.current_level
    
    @property
    def current_level(self):
        return self.levels[self.__lvl_i]
    
    @property
    def next_level(self):
        self.__lvl_i += 1
        return self.current_level

    @property
    def on_last_level(self):
        return self.__lvl_i == len(self.levels) - 1
    
