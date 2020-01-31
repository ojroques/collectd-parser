import logging
import configparser as cp
from os import path, listdir
from datetime import datetime, timedelta


class ParserBase:
    def __init__(self, cfg, plugin_dir):
        base_dir = path.expanduser(cfg.get("GENERAL", "datadir"))
        hostname = cfg.get("GENERAL", "hostname")
        now = datetime.now()
        period = cfg.getint("GENERAL", "period")

        self.data_dir = path.join(base_dir, hostname)
        self.plugin_dirs = [path.join(self.data_dir, p) for p in plugin_dir]

        if period > 0:
            self.start_time = datetime.now() - timedelta(seconds=period)
        else:
            self.start_time = datetime.min

    def get_filenames(self):
        for plugin_dir in self.plugin_dirs:
            filenames = [
                path.join(plugin_dir, f) for f in listdir(plugin_dir)
                if path.isfile(path.join(plugin_dir, f))
            ]
            yield (plugin_dir, filenames)

    def get_directories(self):
        for plugin_dir in listdir(self.data_dir):
            if path.isdir(path.join(self.data_dir, plugin_dir)):
                yield path.join(self.data_dir, plugin_dir)

    def convert_value(self, value, unit):
        if unit == "%":
            return value * 100.
        if unit == "MB":
            return value / 1000000.
        return value

    def get_category(self, filename, categories):
        category = path.basename(path.normpath(filename))[:-11]

        if category in categories:
            return category

        return None
