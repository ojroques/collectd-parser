#!/usr/bin/python3
import logging
import configparser as cp
import numpy as np
from parsers import parserload
from os import path

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
CONFIG_FILE = path.join(path.dirname(path.realpath(__file__)), "default.ini")


def parse_cfg(cfg_path=None):
    config = cp.ConfigParser()

    config.read(CONFIG_FILE)
    logging.info(f"Loaded default config: {CONFIG_FILE}")

    if cfg_path:
        config.read(cfg_path)
        logging.info(f"Loaded config: {cfg_path}")

    return config


def reject_outliers(data, m=3.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m]


def get_stats(values, metric, unit=""):
    stats = {}
    values = np.array(values)
    values_no_outliers = reject_outliers(values)

    stats["metric"] = metric
    stats["unit"] = unit
    stats["samples"] = values.tolist()
    stats["outliers"] = np.setdiff1d(values, values_no_outliers).tolist()
    stats["min"] = float(np.amin(values))
    stats["max"] = float(np.amax(values))
    stats["average"] = float(np.mean(values))
    stats["average_no_outliers"] = float(np.mean(values_no_outliers))
    stats["std"] = float(np.std(values))
    stats["std_no_outliers"] = float(np.std(values_no_outliers))

    return stats


def print_stats(stats):
    metric = stats["metric"]
    unit = stats["unit"]
    nb_samples = len(stats["samples"])
    nb_outliers = len(stats["outliers"])
    ignored = ["metric", "unit", "samples", "outliers"]
    max_key_length = max(len(k) for k in stats if k not in ignored)

    print(f"{metric.upper()} ({nb_samples} elements, {nb_outliers} outliers)")
    for k, v in stats.items():
        if k not in ignored:
            nb_points = max_key_length + 2 - len(k)
            print(f"{k}{'.' * nb_points}{v:.2f} {unit}")


def init(cfg_path=None, output=None, loglevel=logging.INFO):
    logging.getLogger().setLevel(loglevel)

    print(f"COLLECTD RESULTS")
    cfg = parse_cfg(cfg_path)

    parser_load = parserload.ParserLoad(cfg)
    loads = parser_load.parse()
    loads_stats = get_stats(loads, parser_load.metric, parser_load.unit)
    print_stats(loads_stats)


if __name__ == "__main__":
    import argparse

    def main():
        parser = argparse.ArgumentParser(
            description="Parse CSV files produced by collectd")
        parser.add_argument("-c",
                            "--config",
                            metavar="config",
                            help="the path of the config file")
        parser.add_argument("-o",
                            "--output",
                            metavar="filename",
                            help="save raw hiperf output to file")
        parser.add_argument(
            "-l",
            "--loglevel",
            metavar="level",
            help="log level: debug, info (default), warning, error or critical"
        )

        loglevels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }

        cfg_path = parser.parse_args().config
        output = parser.parse_args().output
        loglevel = parser.parse_args().loglevel or "info"

        try:
            loglevel = loglevels[loglevel.lower()]
        except KeyError:
            logging.error(f"log level invalid value '{loglevel}'")
            return

        init(cfg_path, output, loglevel)

    main()
