#!/bin/bash

#screen -d -m 

echo "Stopping any previous iperf3 server running on this machine..."
pkill iperf3

echo
echo "Now starting iperf3 server"
nohup iperf3 --server --json --forceflush | iperf3tocsv.py --output-csv iperf3_server_$(hostname).csv &
