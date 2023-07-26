#!/usr/bin/env python3

"""
    Version: 1.1

    Author: Kirth Gersen
    Date created: 6/5/2016
    Date modified: 9/12/2016
    Python Version: 2.7


    Modified by https://github.com/kbrohman-inrig/iPerf3toCSV

    
    Modified by Francesco Montorsi, as part of https://github.com/f18m/iperf3-continuous-logger 

    NOTE: this script is designed to take input from stdin and produce CSV in output to a specific file
"""

import json
import sys
import csv
import os
import argparse
import datetime

stats = {
    "JsonParseFailures": 0,
    "NumMeasurements": 0,
    "MeasurementsWithErrors": 0,
    "CsvLinesWritten": 0,
}

csv_header = [
    "#timestampTestStart",
    "epochTestStart",
    "IP",
    "LocalPort",
    "RemotePort",
    "Duration(sec)",
    "BytesReceived",
    "BytesSent",
    "BandwidthRx(Bps)",
    "BandwidthTx(Bps)",
]


def eprint(str):
    # all errors go to stderr to avoid corrupting the CSV output (eventually) produced on stdout
    print(str, file=sys.stderr)


def parse_cmdline():
    parser = argparse.ArgumentParser(description="Iperf3 JSON parser")

    # Optional arguments
    parser.add_argument(
        "--output-csv",
        type=str,
        help="The name of the output CSV file; if empty (default) then the CSV is written to stdout",
        default="",
    )

    return parser.parse_args()


def main(output_csv_file):
    global stats

    # highly specific json parser
    # assumes top { } pair are in single line -- this is what iperf3 3.5 produces at least
    jsonstr = ""
    i = 0
    measIdx = 0
    foundStart = False
    for line in sys.stdin:
        i += 1
        if line == "{\n":
            jsonstr = "{"
            foundStart = True
        elif line == "}\n":
            jsonstr += "}"
            if foundStart:
                # the full JSON of an iperf3 measurement has been collected... process it
                process(jsonstr, output_csv_file, measIdx)
                measIdx += 1
            foundStart = False
            jsonstr = ""
        else:
            if foundStart:
                jsonstr += line

    # print on stderr the stats when the stdin is terminated:
    for statName in stats:
        print(f"{statName}: {stats[statName]}", file=sys.stderr)


def process(jsonStr, outFileName, measIndex):
    global stats

    # parse the JSON
    try:
        obj = json.loads(jsonStr)
    except Exception as ex:
        eprint(f"Failed to parse the JSON of an iperf3 measurement: {ex}")
        stats["JsonParseFailures"] += 1
        return False

    # if we get here, parsing was successful.. but iperf3 might have signalled an error:
    stats["NumMeasurements"] += 1
    if "error" in obj:
        eprint(f"Found an iperf3 measurement reporting an error: " + obj["error"])
        stats["MeasurementsWithErrors"] += 1
        return False

    ip = ""
    localPort = 0
    remotePort = 0
    epochTestStart = 0
    durationSec = 0
    bytesRx = 0
    bytesTx = 0

    # extract info from the "start" object
    try:
        ip = obj["start"]["connected"][0]["remote_host"]
        localPort = obj["start"]["connected"][0]["local_port"]
        remotePort = obj["start"]["connected"][0]["remote_port"]
        epochTestStart = obj["start"]["timestamp"][
            "timesecs"
        ]  # this is a Unix epoch actually
    except Exception as ex:
        eprint(
            f"Failed to parse the JSON of an iperf3 measurement: some key related to 'start' object was not found: {ex}"
        )
        stats["JsonParseFailures"] += 1
        return False

    # extract info from the "end" object
    try:
        durationSec = obj["end"]["sum_received"]["seconds"]
        bytesRx = obj["end"]["sum_received"]["bytes"]
        bytesTx = obj["end"]["sum_sent"]["bytes"]
    except Exception as ex:
        eprint(
            f"Failed to parse the JSON of an iperf3 measurement: some key related to 'end' object was not found: {ex}"
        )
        stats["JsonParseFailures"] += 1
        return False

    # IMPORTANT: the bandwidth is measured in bytes-per-second (Bps) and not bit-per-second (bps)
    bandwidthRx = round(bytesRx / durationSec)
    bandwidthTx = round(bytesTx / durationSec)

    # the reason why in each line both the Unix epoch and the human-friendly date/time is reported is to make it easier to
    # process this data in tools that do not support Unix epoch out of the box (like Excel or OpenOffice Calc)
    humanFriendlyTestStartTimestamp = datetime.datetime.fromtimestamp(epochTestStart)
    csv_row = [
        humanFriendlyTestStartTimestamp,
        epochTestStart,
        ip,
        localPort,
        remotePort,
        durationSec,
        bytesRx,
        bytesTx,
        bandwidthRx,
        bandwidthTx,
    ]

    # finally produce the CSV line:
    if not outFileName:
        csvwriter = csv.writer(sys.stdout)
        if measIndex == 0:
            csvwriter.writerow(csv_header)
        csvwriter.writerow(csv_row)
    else:
        # only print the header line if the CSV file does not exist yet... otherwise we assume the header was already provided
        # anyway printing the header in the middle of an initiated CSV file is not a Good Idea
        printHeaderLine = not os.path.isfile(outFileName)
        with open(outFileName, "a", encoding="UTF8", newline="") as f:
            csvwriter = csv.writer(f)
            if printHeaderLine:
                csvwriter.writerow(csv_header)
            csvwriter.writerow(csv_row)

    stats["CsvLinesWritten"] += 1

    return True


if __name__ == "__main__":
    args = parse_cmdline()
    main(args.output_csv)
