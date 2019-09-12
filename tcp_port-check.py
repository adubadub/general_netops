#! /usr/bin/env python3
import socket
import time
import sys
from datetime import datetime

'''
In order to run the script in the background or call with arguments
to avoid need of user input, call the script like below:
'nohup ./tcp_port-check.py [host] [port] [duration (mins)] &'
All output will be appended to nohup.out in local directory
----------------------------------------------------------------
To leverage user inputs, call the script without arguments and 
the 'else' block will execute
'''
if len(sys.argv) > 1:
    host = str(sys.argv[1])
    service = int(sys.argv[2])
    duration = int(sys.argv[3])
else:
    host = str(input("Destination name or IP: "))
    service = int(input("Destination port: "))
    duration = int(input("Duration to run check (mins): "))

seconds = duration * 60
starttime = time.time()
endtime = starttime + seconds

def tcp_port_check(ip, port):
    now = datetime.now().time()
    sess = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sess.settimeout(3)
    
    try:
        sess.connect(( str(ip), int(port) ))
        sess.shutdown(2)
        return f'Success @ {now}'
    except:
        return f'Failure @ {now}'

current_time = time.time()

while current_time < endtime:    
    result = tcp_port_check(host, service)
    current_time = time.time()
    print(result)
    time.sleep(5)

sys.exit()