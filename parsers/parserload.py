import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
from datetime import datetime


class ParserLoad(parserbase.ParserBase):
    def __init__(self, cfg):
        parserbase.ParserBase.__init__(self, cfg, ["load"])
        self.term = f"{cfg.get('LOAD', 'term')}term"

    def parse(self):
        loads = {"cpu load": ("%", [])}

        for _, filenames in self.get_filenames():
            for filename in filenames:
                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        raw_timestamp = int(round(float(row["epoch"])))
                        timestamp = datetime.fromtimestamp(raw_timestamp)

                        if timestamp >= self.start_time:
                            value = self.convert_value(float(row[self.term]),
                                                       "%")
                            loads["cpu load"][1].append(value)

        return loads
