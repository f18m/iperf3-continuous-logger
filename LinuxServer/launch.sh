#!/bin/bash

#screen -d -m 

iperf3 --server --json --logfile server_log.json --forceflush | iperf3tocsv_v2.py measurements.csv
