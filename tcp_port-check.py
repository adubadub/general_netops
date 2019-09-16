#! /usr/bin/env python3
import socket
import time
import sys
import os
import pytz
from datetime import datetime

'''
In order to run the script in the background or call with arguments
to avoid need of user input, call the script like below:
'nohup ./tcp_port-check.py [host] [port] [duration (mins)] [timezone] &'
All output will be appended to nohup.out in local directory
----------------------------------------------------------------
To leverage user inputs, call the script without arguments and 
the 'else' block will execute
'''
if len(sys.argv) > 1:
    host = str(sys.argv[1])
    service = int(sys.argv[2])
    duration = int(sys.argv[3])
    if len(sys.argv) > 4:
        timezone = str(sys.argv[4])
    else:
        timezone = str('Universal')
else:
    host = str(input("Destination name or IP: "))
    service = int(input("Destination port: "))
    duration = int(input("Duration to run check (mins): "))
    print('Timezone format is "Region/Locality", e.g. "America/Chicago". If blank, format will be UTC.')
    timezone = str(input("In which timezone would you like results displayed: "))
    if len(timezone) < 1:
        timezone = ('Universal')

seconds = duration * 60
starttime = time.time()
endtime = starttime + seconds
tz = pytz.timezone(timezone)


def tcp_port_check(ip, port):
    now = datetime.now(tz).time()
    sess = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sess.settimeout(3)
    
    try:
        sess.connect(( str(ip), int(port) ))
        sess.shutdown(2)
        return f'Success @ {now}'
    except:
        return f'Failure @ {now}'

current_time = time.time()

with open('port-check_log.txt', 'w+') as l:

    while current_time < endtime:    
        result = tcp_port_check(host, service)
        current_time = time.time()
        l.write(f'{result}\n')
        print(result)
        pass_count = 0
        fail_count = 0

        if 'Success' in result:
            pass_count = pass_count + 1
        else:
            fail_count = fail_count + 1 

        time.sleep(5)

total = pass_count + fail_count
pass_percent = (pass_count / total) * 100
print(f'{fail_count} failures.')
print(f'{pass_percent}% success rate.')

sys.exit()