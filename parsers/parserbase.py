from os import path, listdir
from datetime import datetime, timedelta


class ParserBase:
    def __init__(self, cfg, hostname, plugin_dirs=[]):
        base_dir = path.expanduser(cfg.get("GENERAL", "datadir"))
        period = cfg.getint("GENERAL", "period")

        self.data_dir = path.join(base_dir, hostname)
        self.plugin_dirs = [
            d for d in self.get_all_plugin_dirs()
            if path.basename(path.normpath(d)) in plugin_dirs
        ]

        if period > 0:
            self.start_time = datetime.now() - timedelta(seconds=period)
        else:
            self.start_time = datetime.min

    def get_all_plugin_dirs(self):
        for plugin_dir in sorted(listdir(self.data_dir)):
            full_plugin_dir = path.join(self.data_dir, plugin_dir)
            if path.isdir(full_plugin_dir):
                yield full_plugin_dir

    def get_all_filenames(self, directories=None):
        _directories = directories or self.plugin_dirs

        for plugin_dir in _directories:
            filenames = sorted(
                path.join(plugin_dir, f) for f in listdir(plugin_dir)
                if path.isfile(path.join(plugin_dir, f)))
            yield (plugin_dir, filenames)

    def get_category(self, filename, categories):
        category = path.basename(path.normpath(filename))[:-11]

        if category in categories:
            return category

        return None

    def convert_value(self, value, unit=""):
        if value.lower() == "nan":
            return 0.0

        value = float(value)

        if unit == "%":
            return value * 100.
        if "MB" in unit:
            return value / 1000000.
        if "Mb" in unit:
            return (value * 8) / 1000000.
        if "GB" in unit:
            return value / 1000000000.

        return value
