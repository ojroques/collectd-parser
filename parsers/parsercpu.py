import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from os import path
from datetime import datetime


class ParserCPU(parserbase.ParserBase):
    def __init__(self, cfg):
        parserbase.ParserBase.__init__(self, cfg, [])
        cpus = json.loads(cfg.get("CPU", "cpus"))

        if cpus:
            self.plugin_dirs = [
                path.join(self.data_dir, f"cpu-{i}") for i in cpus
            ]
        else:
            self.plugin_dirs = [
                path.join(self.data_dir, p) for p in self.get_directories()
                if "cpu" in p
            ]

        self.categories = json.loads(cfg.get("CPU", "categories"))

    def parse(self):
        cpus = {}

        for p in self.plugin_dirs:
            cpu_index = path.basename(path.normpath(p))
            for c in self.categories:
                cpus[f"{cpu_index} {c}"] = ("jiffies", [])

        for plugin_dir, filenames in self.get_filenames():
            cpu_index = path.basename(path.normpath(plugin_dir))

            for filename in filenames:
                metric = None

                for c in self.categories:
                    if c in filename:
                        metric = f"{cpu_index} {c}"
                        break

                if not metric:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        raw_timestamp = int(round(float(row["epoch"])))
                        timestamp = datetime.fromtimestamp(raw_timestamp)

                        if timestamp >= self.start_time:
                            cpus[metric][1].append(float(row["value"]))

        return cpus
