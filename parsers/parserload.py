import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
from datetime import datetime


class ParserLoad(parserbase.ParserBase):
    def __init__(self, cfg, hostname):
        parserbase.ParserBase.__init__(self, cfg, hostname, ["load"])
        self.term = f"{cfg.get('LOAD', 'term')}term"

    def parse(self):
        loads = {"cpu load": ("", [])}

        for _, filenames in self.get_all_filenames():
            for filename in filenames:
                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            value = float(row[self.term])
                            loads["cpu load"][1].append(value)

        return loads
