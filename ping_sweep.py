#!/usr/bin/python3

import multiprocessing
import subprocess
import ipaddress
import argparse
import sys
import os

# Nice comment
def sweeper( job_q , results_q, interface):
    DEVNULL = open(os.devnull,'w')
    while True : 
        ip = job_q.get()
        if ip is None : 
            break ;

        try : 
            subprocess.check_call(['ping' , '-c1' , ip , '-I' , interface],stdout=DEVNULL)
            
            results_q.put(ip)
    
        except:
            pass

if __name__ == '__main__' : 
    
    arg_parser = argparse.ArgumentParser(description='Performs quick ping sweep on a given network')
    arg_parser.add_argument('ip_network' , type=str , help='IP network to scan. Example:10.1.1.0/24')
    arg_parser.add_argument('iface' , type=str , nargs="?" , default="eth0", help='Interface to use. Default is eth0')
    args = arg_parser.parse_args();

    ip_network = ipaddress.IPv4Network(args.ip_network)
    print("Sweeping %s on interface : %s"%(args.ip_network,args.iface))
    interface = args.iface
    jobq = multiprocessing.Queue()
    resultq = multiprocessing.Queue()

    for ipaddr in list(ip_network.hosts()):
        jobq.put(str(ipaddr))

    ProcessQueue = [multiprocessing.Process(target=sweeper , args=(jobq,resultq,interface)) for ipaddr in list(ip_network.hosts())]
    
    for p in ProcessQueue : 
        p.start();
    
    for p in ProcessQueue: 
        jobq.put(None);    

    for p in ProcessQueue:
        p.join()    

    while not resultq.empty():
        ip = resultq.get();

        print('%s\tis up'%(ip))
