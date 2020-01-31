import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from os import path
from datetime import datetime


class ParserVPP(parserbase.ParserBase):
    def __init__(self, cfg):
        parserbase.ParserBase.__init__(self, cfg, [])
        interfaces = json.loads(cfg.get("VPP", "interfaces"))

        if interfaces:
            self.plugin_dirs = [
                path.join(self.data_dir, f"vpp-{i}") for i in interfaces
            ]
        else:
            self.plugin_dirs = [
                path.join(self.data_dir, p) for p in self.get_directories()
                if "vpp" in p
            ]

        self.categories = json.loads(cfg.get("VPP", "categories"))
        self.subcategories = {
            "if_drops": ["packets"],
            "if_punt": ["packets"],
            "if_ip4": ["packets"],
            "if_ip6": ["packets"],
            "if_rx-no-buf": ["packets"],
            "if_rx-miss": ["packets"],
            "if_rx-error": ["packets"],
            "if_tx-error": ["packets"],
            "if_mpls": ["packets"],
            "if_rx": ["packets", "bytes"],
            "if_rx_unicast": ["packets", "bytes"],
            "if_rx_multicast": ["packets", "bytes"],
            "if_rx_broadcast": ["packets", "bytes"],
            "if_tx": ["packets", "bytes"],
            "if_tx_unicast": ["packets", "bytes"],
            "if_tx_multicast": ["packets", "bytes"],
            "if_tx_broadcast": ["packets", "bytes"],
        }
        self.units = {
            "if_drops": {"packets": "packet"},
            "if_punt": {"packets": "packet"},
            "if_ip4": {"packets": "packet"},
            "if_ip6": {"packets": "packet"},
            "if_rx-no-buf": {"packets": "packet"},
            "if_rx-miss": {"packets": "packet"},
            "if_rx-error": {"packets": "packet"},
            "if_tx-error": {"packets": "packet"},
            "if_mpls": {"packets": "packet"},
            "if_rx": {"packets": "packet", "bytes": "MB"},
            "if_rx_unicast": {"packets": "packet", "bytes": "MB"},
            "if_rx_multicast": {"packets": "packet", "bytes": "MB"},
            "if_rx_broadcast": {"packets": "packet", "bytes": "MB"},
            "if_tx": {"packets": "packet", "bytes": "MB"},
            "if_tx_unicast": {"packets": "packet", "bytes": "MB"},
            "if_tx_multicast": {"packets": "packet", "bytes": "MB"},
            "if_tx_broadcast": {"packets": "packet", "bytes": "MB"},
        }

    def parse(self):
        vpps = {}

        for p in self.plugin_dirs:
            interface = path.basename(path.normpath(p))
            for c, scs in self.subcategories.items():
                if c in self.categories:
                    for sc in scs:
                        vpps[f"{interface} {c} {sc}"] = (self.units[c][sc], [])

        for plugin_dir, filenames in self.get_filenames():
            interface = path.basename(path.normpath(plugin_dir))

            for filename in filenames:
                category = None

                for c in self.categories:
                    if c in filename:
                        category = c
                        break

                if not category:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            for subc in self.subcategories[category]:
                                metric = f"{interface} {category} {subc}"
                                value = self.convert_value(
                                    float(row[subc]), self.units[c])
                                vpps[metric][1].append(value)

        return vpps
