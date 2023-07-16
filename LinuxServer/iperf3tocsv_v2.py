#!/usr/bin/env python3

from __future__ import print_function
import json
import sys
import csv
import os

db = {}

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    global db
    """main program"""
        
    if len(sys.argv) == 2:
        if (sys.argv[1] == "-s"):
            fileName="serverLog.csv"
        elif (sys.argv[1] == "-c"):
            fileName="clientLog.csv"
        else:
            sys.exit("Unknow option")
    else:
        sys.exit("No arguments passed")
    
    # accummulate volume per ip in a dict
    db = {}
    
    # highly specific json parser
    # assumes top { } pair are in single line
    jsonstr = ""
    i = 0
    m = False
    for line in sys.stdin:
        i += 1
        if line == "{\n":
            jsonstr = "{"
            m = True
        elif line == "}\n":
            jsonstr += "}"
            if m:
                process(jsonstr, fileName)
            m = False
            jsonstr = ""
        else:
            if m:
                jsonstr += line

def process(js, fileName):
    global db
    try:
        obj = json.loads(js)
    except:
        eprint("bad json")
        pass
        return False 
    try:
        start = []
        end = []
        duration = []
        transfer = []
        bandwidth = []        
        length = len(obj["intervals"])
        
        # caveat: assumes multiple streams are all from same IP so we take the 1st one
        ip = (obj["start"]["connected"][0]["remote_host"]).encode('ascii', 'ignore')
        localPort = obj["start"]["connected"][0]["local_port"]
        remotePort = obj["start"]["connected"][0]["remote_port"]
        dateTime = obj["start"]["timestamp"]["time"]
        
        for i in range(length):
            start.append(obj["intervals"][i]["streams"][0]["start"])
            end.append(obj["intervals"][i]["streams"][0]["end"])
            duration.append(obj["intervals"][i]["streams"][0]["seconds"])
            transfer.append(obj["intervals"][i]["streams"][0]["bytes"])
            bandwidth.append(obj["intervals"][i]["streams"][0]["bits_per_second"])
            
        
        with open(fileName, 'a', encoding='UTF8', newline='') as f:
            csvwriter = csv.writer(f)
            for i in range(length):
                if transfer[i] > 1000000000:
                    transfer[i] /= 1000000000
                    transferNot = "GBytes"
                elif transfer[i] > 1000000:
                    transfer[i] /= 1000000
                    transferNot = "MBytes"
                elif transfer[i] > 1000:
                    transfer[i] /= 1000
                    transferNot = "KBytes"
                else:
                    transferNot = "Bytes"
                    
                if bandwidth[i] > 1000000000:
                    bandwidth[i] /= 1000000000
                    bandwidthNot = "Gbits/sec"
                elif bandwidth[i] > 1000000:
                    bandwidth[i] /= 1000000
                    bandwidthNot = "Mbits/sec"
                elif bandwidth[i] > 1000:
                    bandwidth[i] /= 1000
                    bandwidthNot = "Kbits/sec"
                else:
                    bandwidthNot = "Bits/sec"
                
                
                csvwriter.writerow([ip,localPort,remotePort,start[i],end[i],duration[i],"Seconds",transfer[i],transferNot,bandwidth[i],bandwidthNot,dateTime])
        
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        eprint(exc_type, fname, exc_tb.tb_lineno)
        eprint("error or bogus test:", sys.exc_info()[0])
        pass
    return False

def dumpdb(database):
    """ dump db to text """
    for i in database:
        (s, r) = database[i]
        print("%s, %d , %d " % (i, s, r))

if __name__ == '__main__':
    main()