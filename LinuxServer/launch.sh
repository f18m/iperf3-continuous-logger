#!/bin/bash

#screen -d -m 

pkill iperf3
nohup iperf3 --server --json --forceflush | iperf3tocsv_v3.py --output-csv iperf3_server_$(hostname).csv &
