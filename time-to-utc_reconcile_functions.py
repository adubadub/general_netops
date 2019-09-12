#! /usr/bin/env python3
# imports
import subprocess
from netmiko import Netmiko, ConnectHandler
import datetime
from dateutil import parser

# local variables
local_time = subprocess.check_output("date").decode("utf-8")
utc_time = str(datetime.datetime.utcnow())

# datetime strip date or time function
"""
The following function is not used below, but I found it useful when
playing around with different ways to leverage specific datetime values
"""
def datetime_strip(n, strip):
    if strip == 'time':
        date_time = parser.parse(n)
        norm_date = date_time.strftime('%Y-%m-%d')
        return norm_date
    if strip == 'date':
        date_time = parser.parse(n)
        norm_time = date_time.strftime('%H:%M')
        return norm_time

# date and time formatting function
def format_datetime(n):
    datetime_value = parser.parse(n)
    normalized_datetime = datetime_value.strftime('%H:%M:%S:%f %Y-%m-%d')
    return normalized_datetime

# offset-from-utc reconcile function
def utc_offset_reconcile(n, offset):
    time_offset_split = offset.split(':')
    offset_hours = int(time_offset_split[0])
    offset_minutes = int(time_offset_split[1])
    offset_seconds = int(time_offset_split[2])
    time_offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes, seconds=offset_seconds)
    normal_datetime = parser.parse(n)
    normalized_datetime = normal_datetime - time_offset
    normalized_datetime = normalized_datetime.strftime('%H:%M:%S.%f %Y-%m-%d')
    return normalized_datetime 

# find offset-from-utc function
def find_offset_fromutc(n):
    time_split = n.split()
    current_time = []
    utc_split = utc_time.split()
    current_utc = []

    for i in time_split:
        if ':' in i:
            current_time.append(i)
    for i in utc_split:
        if ':' in i:
            current_utc.append(i)

    current_time = ''.join(current_time)
    current_utc = ''.join(current_utc)
    current_time_split = current_time.split(':')
    current_utc_split = current_utc.split(':')

    time_hour = int(current_time_split[0])
    time_minute = int(current_time_split[1])
    time_second = int(current_time_split[2])
    utc_hour = int(current_utc_split[0])
    utc_minute = int(current_utc_split[1])
    utc_second = int(current_utc_split[2])
    offset_hour = utc_hour - time_hour
    offset_minute = utc_minute - time_minute
    offset_second = utc_second - time_second
    offset = f'{offset_hour}:{offset_minute}:{offset_second}'
    return offset

# formatted utc time
utc_time = format_datetime(utc_time)
# local-time offset from utc
local_offset = find_offset_fromutc(local_time)

# get cisco device time, format time, find device offset,
## get logs and define output example
### note: netmiko used below (stripped netmiko code above)
"""
with ConnectHandler(**device) as channel:
    '''
    Below we get the device time, normalize the time format and then call 
    the find_offset_fromutc function to get the offset of device time from utc
    '''
    clock = channel.send_command('show clock')
    clock = format_datetime(clock)
    dev_offset = find_offset_fromutc(clock)

    '''
    Below we're just extracting and formatting desired syslog entries
    '''
    cmd1 = 'show ip int br'
    int_out = channel.send_command(cmd1)
    int_split = int_out.split()
    tun_list = []
    tunnel_description = {}
    
    for i in int_split:
        if 'Tunnel' in i:
            tun_list.append(i)

    for i in tun_list:
        cmd = f'show run int {i}'
        config = channel.send_command(cmd)
        config_split = config.splitlines()
        
        for idx, val in enumerate(config_split):
            if 'description' in val:
                desc = config_split[idx]
                desc_split = desc.split()
                for idx, val in enumerate(desc_split):
                    if 'description' in val:
                        int_desc = desc_split[idx + 1:]
                        description = ','.join(int_desc).replace(',', ' ')

        tunnel_description[i] = description       

    for i in tun_list:
        cmd = f'show logg | i {i}'
        tun_out = channel.send_command(cmd)
        tun_split = tun_out.split()

        for idx, val in enumerate(tun_split):
            if 'OSPF' in val:
                if 'LOADING' in tun_split[idx:idx + 10]:
                    del tun_split[idx:idx + 12]
                else:
                    del tun_split[idx:idx + 17]
        
        '''
        Below we're formatting and defining output
        '''
        for idx, val in enumerate(tun_split):
            if val == 'down':
                tunnel = tun_split[idx - 4].replace(',', '')
                time_down = tun_split[idx - 13:idx - 10]
                time_down = ', '.join(time_down).replace(',', '')
                
                '''
                Here we first reconcile our formatted log/device timestamps with utc 
                and then take that time and reconcile with our local time.
                The output is then the true time an event was logged on a device 
                anywhere in the world, represented in our current local time.
                '''
                time_down = utc_offset_reconcile(time_down, dev_offset)
                time_down = utc_offset_reconcile(time_down, local_offset)
                print(f'{tunnel} ({tunnel_description[i]}) DOWN @ {time_down}')
            if val == 'up':
                tunnel = tun_split[idx - 4].replace(',', '')
                time_up = tun_split[idx - 13:idx - 10]
                time_up = ', '.join(time_up).replace(',', '')
                
                '''
                Here we first reconcile our formatted log/device timestamps with utc 
                and then take that time and reconcile with our local time.
                The output is then the true time an event was logged on a device 
                anywhere in the world, represented in our current local time.
                '''
                time_up = utc_offset_reconcile(time_up, dev_offset)
                time_up = utc_offset_reconcile(time_up, local_offset)
                print(f'{tunnel} ({tunnel_description[i]}) UP   @ {time_up}')

    channel.disconnect()
"""
