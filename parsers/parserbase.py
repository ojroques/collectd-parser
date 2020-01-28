import logging
import configparser as cp
from os import path, listdir


class ParserBase:
    def __init__(self, cfg, plugin_dir, metric, unit=""):
        base_dir = path.expanduser(cfg.get("GENERAL", "datadir"))
        hostname = cfg.get("GENERAL", "hostname")

        self.metric = metric
        self.unit = unit
        self.data_dir = path.join(base_dir, hostname)
        self.plugin_dirs = [path.join(self.data_dir, p) for p in plugin_dir]
        self.interval = cfg.getint("GENERAL", "interval")

    def get_filenames(self):
        for plugin_dir in self.plugin_dirs:
            filenames = [
                path.join(plugin_dir, f) for f in listdir(plugin_dir)
                if path.isfile(path.join(plugin_dir, f))
            ]
            yield (plugin_dir, filenames)
