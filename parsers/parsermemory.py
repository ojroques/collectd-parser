import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from datetime import datetime


class ParserMemory(parserbase.ParserBase):
    def __init__(self, cfg, hostname):
        parserbase.ParserBase.__init__(self, cfg, hostname, ["memory"])
        self.categories = json.loads(cfg.get("MEMORY", "categories"))

    def parse(self):
        memorys = {f"memory {c}": ("MB", []) for c in self.categories}

        for _, filenames in self.get_all_filenames():
            for filename in filenames:
                category = self.get_category(filename, self.categories)

                if not category:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            value = self.convert_value(row["value"], "MB")
                            memorys[f"memory {category}"][1].append(value)

        return memorys
