import logging
import configparser as cp
import parsers.parserbase as parserbase
import csv
import json
from os import path
from datetime import datetime


class ParserVPPHICN(parserbase.ParserBase):
    def __init__(self, cfg, hostname):
        faces = json.loads(cfg.get("VPP_HICN", "faces"))
        parserbase.ParserBase.__init__(self, cfg, hostname,
                                       [f"vpp_hicn-{i}" for i in faces])

        if not self.plugin_dirs:
            self.plugin_dirs = [
                p for p in self.get_all_plugin_dirs()
                if "vpp_hicn" in path.basename(path.normpath(p))
            ]

        self.node = None
        if cfg.getboolean("VPP_HICN", "node"):
            self.node = path.join(self.data_dir, "vpp_hicn-node")

        self.face_categories = json.loads(
            cfg.get("VPP_HICN", "face_categories"))
        self.node_categories = json.loads(
            cfg.get("VPP_HICN", "node_categories"))
        self.node_subcategories = {
            "pkts_processed": "packets",
            "pkts_interest_count": "packets",
            "pkts_data_count": "packets",
            "pkts_from_cache_count": "packets",
            "pkts_no_pit_count": "packets",
            "pit_expired_count": "interests",
            "cs_expired_count": "data",
            "cs_lru_count": "data",
            "pkts_drop_no_buf": "packets",
            "interests_aggregated": "interests",
            "interests_retx": "interests",
            "interests_hash_collision": "interests",
            "pit_entries_count": "interests",
            "cs_entries_count": "data",
            "cs_entries_ntw_count": "data",
        }
        self.node_units = {
            "pkts_processed": "packet",
            "pkts_interest_count": "packet",
            "pkts_data_count": "packet",
            "pkts_from_cache_count": "packet",
            "pkts_no_pit_count": "packet",
            "pit_expired_count": "interest",
            "cs_expired_count": "data",
            "cs_lru_count": "data",
            "pkts_drop_no_buf": "packet",
            "interests_aggregated": "interest",
            "interests_retx": "interest",
            "interests_hash_collision": "interest",
            "pit_entries_count": "interest",
            "cs_entries_count": "data",
            "cs_entries_ntw_count": "data",
        }

    def parse_node(self):
        if not self.node:
            return

        node_values = {
            f"vpp_hicn-node {c}": (self.node_units[c], [])
            for c in self.node_categories
        }

        for _, filenames in self.get_all_filenames([self.node]):
            for filename in filenames:
                category = self.get_category(filename, self.node_categories)

                if not category:
                    continue

                subc = self.node_subcategories[category]
                unit = self.node_units[category]

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            value = self.convert_value(row[subc], unit)
                            node_values[f"vpp_hicn-node {category}"][1].append(value)

        return node_values

    def parse_faces(self):
        faces = {}
        units = {"packets": "packet/s", "bytes": "Mb/s"}

        for p in self.plugin_dirs:
            face = path.basename(path.normpath(p))
            for c in self.face_categories:
                for subc, unit in units.items():
                    faces[f"{face} {c} {subc}"] = (unit, [])

        for plugin_dir, filenames in self.get_all_filenames():
            face = path.basename(path.normpath(plugin_dir))

            for filename in filenames:
                category = self.get_category(filename, self.face_categories)

                if not category:
                    continue

                with open(filename, "r") as file:
                    csv_reader = csv.DictReader(file, delimiter=',')

                    for row in csv_reader:
                        timestamp = datetime.fromtimestamp(float(row["epoch"]))

                        if timestamp >= self.start_time:
                            for subc, unit in units.items():
                                metric = f"{face} {category} {subc}"
                                value = self.convert_value(row[subc], unit)
                                faces[metric][1].append(value)

        return faces
