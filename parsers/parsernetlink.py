import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from os import path
from datetime import datetime


class ParserNetlink(parserbase.ParserBase):
    def __init__(self, cfg, hostname):
        parserbase.ParserBase.__init__(self, cfg, hostname)
        interfaces = json.loads(cfg.get("NETLINK", "interfaces"))

        if interfaces:
            self.plugin_dirs = [
                path.join(self.data_dir, f"netlink-{i}") for i in interfaces
            ]
        else:
            self.plugin_dirs = [
                path.join(self.data_dir, p) for p in self.get_directories()
                if "netlink" in p
            ]

        self.categories = json.loads(cfg.get("NETLINK", "categories"))
        self.subcategories = {
            "if_collisions": ["value"],
            "if_dropped": ["rx", "tx"],
            "if_errors": ["rx", "tx"],
            "if_multicast": ["value"],
            "if_octets": ["rx", "tx"],
            "if_packets": ["rx", "tx"],
            "if_rx_errors-crc": ["value"],
            "if_rx_errors-fifo": ["value"],
            "if_rx_errors-frame": ["value"],
            "if_rx_errors-length": ["value"],
            "if_rx_errors-missed": ["value"],
            "if_rx_errors-over": ["value"],
            "if_tx_errors-aborted": ["value"],
            "if_tx_errors-carrier": ["value"],
            "if_tx_errors-fifo": ["value"],
            "if_tx_errors-heartbeat": ["value"],
            "if_tx_errors-window": ["value"],
            "ipt_bytes-qdisc-fq_codel-0:0": ["value"],
            "ipt_bytes-qdisc-mq-0:0": ["value"],
            "ipt_packets-qdisc-fq_codel-0:0": ["value"],
            "ipt_packets-qdisc-mq-0:0": ["value"],
        }
        self.subcategories.update(
            {f"ipt_bytes-class-mq-0:{i}": ["value"]
             for i in range(1, 9)})
        self.subcategories.update(
            {f"ipt_packets-class-mq-0:{i}": ["value"]
             for i in range(1, 9)})
        self.units = {
            "if_collisions": "packet/s",
            "if_dropped": "packet/s",
            "if_errors": "packet/s",
            "if_multicast": "packet/s",
            "if_octets": "MB/s",
            "if_packets": "packet/s",
            "if_rx_errors-crc": "packet/s",
            "if_rx_errors-fifo": "packet/s",
            "if_rx_errors-frame": "packet/s",
            "if_rx_errors-length": "packet/s",
            "if_rx_errors-missed": "packet/s",
            "if_rx_errors-over": "packet/s",
            "if_tx_errors-aborted": "packet/s",
            "if_tx_errors-carrier": "packet/s",
            "if_tx_errors-fifo": "packet/s",
            "if_tx_errors-heartbeat": "packet/s",
            "if_tx_errors-window": "packet/s",
            "ipt_bytes-qdisc-fq_codel-0:0": "MB/s",
            "ipt_bytes-qdisc-mq-0:0": "MB/s",
            "ipt_packets-qdisc-fq_codel-0:0": "packet/s",
            "ipt_packets-qdisc-mq-0:0": "packet/s",
        }
        self.units.update(
            {f"ipt_bytes-class-mq-0:{i}": "MB/s"
             for i in range(1, 9)})
        self.units.update(
            {f"ipt_packets-class-mq-0:{i}": "packet/s"
             for i in range(1, 9)})

    def parse(self):
        netlinks = {}

        for p in self.plugin_dirs:
            interface = path.basename(path.normpath(p))
            for c, scs in self.subcategories.items():
                if c in self.categories:
                    for sc in scs:
                        netlinks[f"{interface} {c} {sc}"] = (self.units[c], [])

        for plugin_dir, filenames in self.get_filenames():
            interface = path.basename(path.normpath(plugin_dir))

            for filename in filenames:
                category = self.get_category(filename, self.categories)

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
                                    float(row[subc]), self.units[category])
                                netlinks[metric][1].append(value)

        return netlinks
