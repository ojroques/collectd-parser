# collectd-parser

Parsers for [collectd](https://github.com/collectd/collectd). The [CSV plugin](https://collectd.org/wiki/index.php/Plugin:CSV) must be enabled. Currently there are parsers for:
* [cpu](https://collectd.org/wiki/index.php/Plugin:CPU)
* [cpu load](https://collectd.org/wiki/index.php/Plugin:Load)
* [netlink](https://collectd.org/wiki/index.php/Plugin:Netlink)
* [memory](https://collectd.org/wiki/index.php/Plugin:Memory)

## Requirements
* Python 3.6+
* Numpy

## Usage
Parsers are present in [parsers](parsers). `parse_collectd.py` runs all of them, prints the results and can save them is JSON format:
```sh
./parse_collectd.py -o results.json
```

You can change settings by editing [default.ini](default.ini) or by passing a custom config file:
```sh
./parse_collectd -c config.ini
```

It is also possible to print the results from a JSON file:
```sh
./parse_collectd -i results.json
```

To see all available options:
```sh
./parse_collectd -h
```

## Example

```sh
oroques@oroques-vm:~/Documents/collectd-setup$ ./parse_collectd.py -o results.json
[INFO] Loaded default config: /home/oroques/Documents/collectd-setup/default.ini
COLLECTD RESULTS
Start: 2020-01-29 12:54:16
End: 2020-01-29 13:54:16
----------------------------------------

CPU LOAD (360 elements, 26 outliers)
min..................0.00 
max..................82.00 
average..............11.38 
average_no_outliers..7.35 
std..................14.13 
std_no_outliers......6.43 

CPU-0 USER (360 elements, 50 outliers)
min..................230348.00 jiffies
max..................230865.00 jiffies
average..............230495.88 jiffies
average_no_outliers..230368.19 jiffies
std..................181.44 jiffies
std_no_outliers......12.04 jiffies

MEMORY USED (360 elements, 92 outliers)
min..................6982.91 MB
max..................7082.56 MB
average..............7011.60 MB
average_no_outliers..6999.00 MB
std..................26.63 MB
std_no_outliers......1.98 MB

NETLINK-ENS160 IF_OCTETS RX (360 elements, 56 outliers)
min..................128.10 MB
max..................129.75 MB
average..............128.67 MB
average_no_outliers..128.52 MB
std..................0.45 MB
std_no_outliers......0.30 MB

NETLINK-ENS160 IF_OCTETS TX (360 elements, 142 outliers)
min..................108.73 MB
max..................113.79 MB
average..............110.00 MB
average_no_outliers..108.94 MB
std..................1.56 MB
std_no_outliers......0.00 MB

----------------------------------------
[INFO] Saving results into results.json
```
