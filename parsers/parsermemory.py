import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from datetime import datetime


class ParserMemory(parserbase.ParserBase):
    def __init__(self, cfg):
        parserbase.ParserBase.__init__(self, cfg, ["memory"])
        self.categories = json.loads(cfg.get("MEMORY", "categories"))

    def parse(self):
        memorys = {f"memory {c}": ("MB", []) for c in self.categories}

        for _, filenames in self.get_filenames():
            for filename in filenames:
                metric = None

                for c in self.categories:
                    if c in filename:
                        metric = f"memory {c}"
                        break

                if not metric:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        raw_timestamp = int(round(float(row["epoch"])))
                        timestamp = datetime.fromtimestamp(raw_timestamp)

                        if timestamp >= self.start_time:
                            value = self.convert_value(float(row["value"]),
                                                       "MB")
                            memorys[metric][1].append(value)

        return memorys
