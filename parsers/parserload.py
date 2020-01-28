import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv


class ParserLoad(parserbase.ParserBase):
    def __init__(self, cfg):
        parserbase.ParserBase.__init__(self, cfg, ["load"], "cpu load")
        self.period = f"{cfg.get('LOAD', 'period')}term"

    def parse(self):
        loads = []

        for _, filenames in self.get_filenames():
            for filename in filenames:
                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')
                    for row in csv_reader:
                        loads.append(float(row[self.period]))

        return loads
