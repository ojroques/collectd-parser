import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from os import path
from datetime import datetime


class ParserCPU(parserbase.ParserBase):
    def __init__(self, cfg, hostname):
        cpus = json.loads(cfg.get("CPU", "cpus"))
        parserbase.ParserBase.__init__(self, cfg, hostname,
                                       [f"cpu-{i}" for i in cpus])

        if not self.plugin_dirs:
            self.plugin_dirs = [
                p for p in self.get_all_plugin_dirs()
                if "cpu" in path.basename(path.normpath(p))
            ]

        self.categories = json.loads(cfg.get("CPU", "categories"))

    def parse(self):
        cpus = {}

        for p in self.plugin_dirs:
            cpu_index = path.basename(path.normpath(p))
            for c in self.categories:
                cpus[f"{cpu_index} {c}"] = ("jiffy", [])

        for plugin_dir, filenames in self.get_all_filenames():
            cpu_index = path.basename(path.normpath(plugin_dir))

            for filename in filenames:
                category = self.get_category(filename, self.categories)

                if not category:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            cpus[f"{cpu_index} {category}"][1].append(
                                float(row["value"]))

        return cpus
