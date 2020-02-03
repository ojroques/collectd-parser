# collectd-parser

Parsers for [collectd](https://github.com/collectd/collectd). The [CSV plugin](https://collectd.org/wiki/index.php/Plugin:CSV) must be enabled. Currently there are parsers for:
* [cpu](https://collectd.org/wiki/index.php/Plugin:CPU)
* [cpu load](https://collectd.org/wiki/index.php/Plugin:Load)
* [netlink](https://collectd.org/wiki/index.php/Plugin:Netlink)
* [memory](https://collectd.org/wiki/index.php/Plugin:Memory)
* vpp

## Requirements
* Python 3.6+
* Numpy

## Usage
Parsers are present in [parsers](parsers). `parse_collectd.py` runs all of them for a given host, prints the results and can save them is JSON format:
```sh
./parse_collectd.py myhost -o results.json
```

You can change settings by editing [default.ini](default.ini) or by passing a custom config file:
```sh
./parse_collectd.py myhost -c config.ini
```

It is also possible to print the results from a JSON file:
```sh
./parse_collectd.py results.json
```

To see all available options:
```sh
./parse_collectd.py -h
```

## Example

```sh
oroques@oroques-vm:~/Documents/collectd-parser$ ./parse_collectd.py oroques-vm -o results.json
[INFO] Loaded default config: /home/oroques/Documents/collectd-parser/default.ini
COLLECTD RESULTS
Host: oroques-vm
Start: 2020-02-03 13:06:31
End: 2020-02-03 14:06:31
----------------------------------------

CPU LOAD (361 elements, 42 outliers)
min..................0.01 
max..................4.87 
average..............2.61 
average_no_outliers..3.69 
std..................1.77 
std_no_outliers......0.85 

CPU-0 CPU-USER (360 elements, 0 outliers)
min..................109974.00 jiffy
max..................159915.00 jiffy
average..............137595.98 jiffy
average_no_outliers..137595.98 jiffy
std..................14709.83 jiffy
std_no_outliers......14709.83 jiffy

MEMORY MEMORY-USED (361 elements, 79 outliers)
min..................6788.94 MB
max..................7730.27 MB
average..............7339.24 MB
average_no_outliers..7489.20 MB
std..................376.85 MB
std_no_outliers......293.38 MB

NETLINK-ENS160 IF_OCTETS RX (12 elements, 0 outliers)
min..................845.38 MB/s
max..................845.45 MB/s
average..............845.41 MB/s
average_no_outliers..845.41 MB/s
std..................0.02 MB/s
std_no_outliers......0.02 MB/s

NETLINK-ENS160 IF_OCTETS TX (12 elements, 0 outliers)
min..................70.60 MB/s
max..................70.88 MB/s
average..............70.75 MB/s
average_no_outliers..70.75 MB/s
std..................0.10 MB/s
std_no_outliers......0.10 MB/s

----------------------------------------
[INFO] Saving results into results.json
```
