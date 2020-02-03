#!/usr/bin/python3
import logging
import json
import configparser as cp
import numpy as np
from os import path
from datetime import datetime, timedelta
from parsers import parserload, parsermemory, parsernetlink, parsercpu, parservpp

logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
CONFIG_FILE = path.join(path.dirname(path.realpath(__file__)), "default.ini")


def save_dict(d, filename):
    logging.info(f"Saving results into {filename}")
    with open(filename, "w") as file:
        json.dump(d, file, indent=4)


def print_json(filename):
    with open(filename, "r") as file:
        all_results = json.load(file)

    start_time = datetime.fromtimestamp(all_results.pop("start_timestamp"))
    end_time = datetime.fromtimestamp(all_results.pop("end_timestamp"))

    print(f"COLLECTD RESULTS from {filename}")
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("----------------------------------------\n")

    for all_stats in all_results.values():
        print_stats(all_stats)

    print("----------------------------------------")


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


def get_stats(results):
    all_stats = {}

    for metric, (unit, values) in results.items():
        stats = {}
        values = np.array(values)
        values_no_outliers = reject_outliers(values)

        stats["unit"] = unit
        stats["samples"] = values.tolist()
        stats["outliers"] = np.setdiff1d(values, values_no_outliers).tolist()
        stats["min"] = float(np.amin(values))
        stats["max"] = float(np.amax(values))
        stats["average"] = float(np.mean(values))
        stats["average_no_outliers"] = float(np.mean(values_no_outliers))
        stats["std"] = float(np.std(values))
        stats["std_no_outliers"] = float(np.std(values_no_outliers))

        all_stats[metric] = stats

    return all_stats


def print_stats(all_stats, end="\n"):
    for metric, stats in all_stats.items():
        unit = stats["unit"]
        nb_samples = len(stats["samples"])
        nb_outliers = len(stats["outliers"])
        ignored = ["unit", "samples", "outliers"]
        max_key_length = max(len(k) for k in stats if k not in ignored)

        print(
            f"{metric.upper()} ({nb_samples} elements, {nb_outliers} outliers)"
        )
        for k, v in stats.items():
            if k not in ignored:
                nb_points = max_key_length + 2 - len(k)
                print(f"{k}{'.' * nb_points}{v:.2f} {unit}")

        print(end, end='')


def init(hostname, cfg_path=None, results=None, output=None, loglevel=logging.INFO):
    logging.getLogger().setLevel(loglevel)

    if results:
        print_json(results)
        return

    cfg = parse_cfg(cfg_path)
    all_results = {}
    end_time = datetime.now()
    period = cfg.getint("GENERAL", "period")
    enabled = json.loads(cfg.get("GENERAL", "enabled"))

    if period > 0:
        start_time = end_time - timedelta(seconds=period)
    else:
        start_time = datetime.min

    all_results["start_timestamp"] = start_time.timestamp()
    all_results["end_timestamp"] = end_time.timestamp()

    print(f"COLLECTD RESULTS")
    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("----------------------------------------\n")

    # CPU LOAD
    if "load" in enabled:
        parser_load = parserload.ParserLoad(cfg, hostname)
        loads = parser_load.parse()
        loads_stats = get_stats(loads)
        print_stats(loads_stats)
        all_results["cpu load"] = loads_stats

    # CPU
    if "cpu" in enabled:
        parser_cpu = parsercpu.ParserCPU(cfg, hostname)
        cpus = parser_cpu.parse()
        cpus_stats = get_stats(cpus)
        print_stats(cpus_stats)
        all_results["cpu"] = cpus_stats

    # MEMORY
    if "memory" in enabled:
        parser_memory = parsermemory.ParserMemory(cfg, hostname)
        memorys = parser_memory.parse()
        memorys_stats = get_stats(memorys)
        print_stats(memorys_stats)
        all_results["memory"] = memorys_stats

    # NETLINK
    if "netlink" in enabled:
        parser_netlink = parsernetlink.ParserNetlink(cfg, hostname)
        netlinks = parser_netlink.parse()
        netlinks_stats = get_stats(netlinks)
        print_stats(netlinks_stats)
        all_results["netlink"] = netlinks_stats

    # VPP
    if "vpp" in enabled:
        parser_vpp = parservpp.ParserVPP(cfg, hostname)
        vpps = parser_vpp.parse()
        vpps_stats = get_stats(vpps)
        print_stats(vpps_stats)
        all_results["vpp"] = vpps_stats

    print("----------------------------------------")

    if output:
        save_dict(all_results, output)


if __name__ == "__main__":
    import argparse

    def main():
        parser = argparse.ArgumentParser(
            description="Parse CSV files produced by collectd")
        parser.add_argument("hostname",
                            metavar="hostname",
                            help="host to parse")
        parser.add_argument("-c",
                            "--config",
                            metavar="config",
                            help="the path of the config file")
        parser.add_argument("-o",
                            "--output",
                            metavar="results.json",
                            help="save collectd results into a JSON file")
        parser.add_argument("-i",
                            "--input",
                            metavar="results.json",
                            help="print collectd results from a JSON file")
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

        hostname = parser.parse_args().hostname
        cfg_path = parser.parse_args().config
        output = parser.parse_args().output
        results = parser.parse_args().input
        loglevel = parser.parse_args().loglevel or "info"

        try:
            loglevel = loglevels[loglevel.lower()]
        except KeyError:
            logging.error(f"log level invalid value '{loglevel}'")
            return

        init(hostname, cfg_path, results, output, loglevel)

    main()
