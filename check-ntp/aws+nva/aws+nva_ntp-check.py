#! /usr/bin/env python3
if True: # imports
    import json
    import paramiko
    import time
    import subprocess
    import sys
    from datetime import datetime
    import pypsrp
    from pypsrp.client import Client
if True: # set env variables
    with open('aws+nva_ntp-check.json') as f:
        js              = json.load(f)
        device_dict     = js['VPCS']
        primary_dc      = js['PRIMARY_DC']
        svc_act_un      = js['SVC_UN']
        svc_act_pwd     = js['SVC_PWD']
        netadmin_un     = js['NETADMIN_UN']
        netadmin_pwd    = js['NETADMIN_PWD']
if True: # set local variables
    days = [
        'monday', 'mon', 'tuesday', 'tue', 'wednesday', 'wed, ''thursday', 'thu',
        'friday', 'fri', 'saturday', 'sat', 'sunday', 'sun']
    months = [
        'january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr', 'may', 
        'june', 'jun', 'july', 'jul', 'august', 'aug', 'september', 'sep', 
        'october', 'oct', 'november', 'nov', 'december', 'dec']
if True: # define FormatTime function
    def FormatTime(timestring):
        timestring = timestring.replace(',', '')
        timestring_split = timestring.split()
        new_timestring = []

        for i in timestring_split:
            try:
                if int(i) > 31:
                    new_timestring.insert(4, i)
                else:
                    new_timestring.insert(2, i)
            except:
                if i.lower() in days:
                    i = ''.join([char for char in i][0:3])
                    new_timestring.insert(0, i)
                if i.lower() in months:
                    i = ''.join([char for char in i][0:3])
                    new_timestring.insert(1, i)
                if ':' in i:
                    if 'pm' in timestring.lower():
                        i_split = i.split(':')
                        hour = int(i_split[0])
                        hour = hour + 12
                        i_split[0] = str(hour)
                        i = ':'.join(i_split)
                        new_timestring.insert(3, i)
                    else:
                        new_timestring.insert(3, i)
                if 'utc' in i.lower():
                    pass
                if 'am' in i.lower():
                    pass

        new_timestring = ' '.join(new_timestring)
        dev_dt = datetime.strptime(new_timestring, "%a %b %d %H:%M:%S %Y")  
        return dev_dt
if True: # define ConvertTD (timedelta) function
    def ConvertTD(duration):
        days, seconds = duration.days, duration.seconds
        days_to_seconds = days * 86400
        total_seconds = days_to_seconds + seconds
        offset = []

        if total_seconds < 86399:
            if total_seconds < 59:
                if total_seconds > 2:
                    offset.append('seconds')
                    offset.append(duration.seconds)
                else:
                    offset.append('GOOD')
                    offset.append(duration.seconds)
            else:
                offset.append('minutes')
                offset.append(total_seconds // 60)
        else:
            offset.append('days')
            offset.append(duration.days)

        return offset
if True: # define GetOffset function
    def GetOffset(devtime, truetime):
        dev_dt_offset = truetime - devtime
        dev_offset = ConvertTD(dev_dt_offset)
        return dev_offset
if True: # define Subprocess function
    def Sprocess(COMMAND):
        PROCESS = subprocess.Popen(COMMAND, stdout=subprocess.PIPE, shell=True)
        OUTPUT = PROCESS.communicate()[0].strip()
        return OUTPUT
if True: # define send exec command (Exec) function
    def Exec(ADDRESS, USERNAME, PASSWORD, COMMAND):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ADDRESS, port=22, username=USERNAME, password=PASSWORD, look_for_keys=False, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(COMMAND)
        output = (stdout.read()).decode("utf-8")
        
        stderr.close()
        stdout.close()
        stdin.close()
        client.close()
        return output
if True: # define WindowsConnect function
    def WindowsConnect(DC, UN, PWD, COMMANDS):
        dc_client = Client(DC, username=UN,
            password=PWD,
            cert_validation=False,
            ssl=False
            )
        dc_date = dc_client.execute_cmd(COMMANDS)
        dc_date = dc_date[0].strip()
        return dc_date
if True: # Code
    for vpc in device_dict:
        # set working variables
        vpc_dc_ips = []
        vpc_ntp_ips = []
        vals = device_dict[vpc]
        vpc_name = vals['NAME']
        vpc_acct = vals['ACCT']
        vpc_dcs  = vals['DCS']
        vpc_fws  = vals['FWS']
        vpc_lbs  = vals['LBS']
        if vpc_acct == 'sandbox':
            awscreds = 'sandbox'
        if vpc_acct == 'prod':
            awscreds = 'production'
        if vpc_acct == 'mgmt':
            awscreds = 'management'

        # get AWS VPC DHCP-OPTION settings
        vpc_verbose = Sprocess(f'''aws ec2 describe-vpcs --profile {awscreds} \
            --filters "Name=tag:Name,Values={vpc_name}"
            ''').strip().decode().split()
        for i in vpc_verbose:
            if 'dopt' in i:
                vpc_dhcpid = i.strip(',').strip('"')
        vpc_dhcp = Sprocess(f'''aws ec2 describe-dhcp-options --profile {awscreds} \
            --dhcp-options-ids {vpc_dhcpid}
            ''').strip().decode().split()
        for idx, val in enumerate(vpc_dhcp):
            if 'domain-name' in val and 'servers' not in val:
                dn = vpc_dhcp[idx + 5].strip('"')
            if 'domain-name-servers' in val:
                dc_idx_start = vpc_dhcp[idx:]
                for v in dc_idx_start:
                    if 'Key' in v:
                        dc_idx_end = dc_idx_start.index(v)
                dc_idxs = vpc_dhcp[idx:idx + dc_idx_end]
                dcs = []
                for i, v in enumerate(dc_idxs):
                    if '"Value"' in v:
                        dcs.append(dc_idxs[i + 1])
                for ip in dcs:
                    vpc_dc_ips.append(ip.strip('"'))
            if 'ntp' in val:
                ntp_idx_start = vpc_dhcp[idx:]
                for v in ntp_idx_start:
                    if 'Dhcp' in v:
                        ntp_idx_end = ntp_idx_start.index(v)
                ntp_idxs = vpc_dhcp[idx:idx + ntp_idx_end]
                ntp = []
                for i, v in enumerate(ntp_idxs):
                    if '"Value"' in v:
                        ntp.append(ntp_idxs[i + 1])
                for ip in ntp:
                    vpc_ntp_ips.append(ip.strip('"'))
        
        # get DC NTP status and drift
        dc_ntp = {}
        dc_ntp_status = {}
        for dc in vpc_dcs:
            dc_ntp[dc] = []
            command = 'w32tm /query /peers'
            ntp_settings_verbose = WindowsConnect(dc, svc_act_un, svc_act_pwd, command)
            ntp_settings_split = ntp_settings_verbose.split()
            
            for idx, val in enumerate(ntp_settings_split):
                if 'Peer:' in val:
                    server = ntp_settings_split[idx + 1]
                    try:
                        server_split = server.split(',')
                        server = server_split[0]
                        dc_ntp[dc] = dc_ntp[dc] + [server]
                    except:
                        dc_ntp[dc] = dc_ntp[dc] + [server]

            command = 'powershell.exe date'
            dc_time = WindowsConnect(dc, svc_act_un, svc_act_pwd, command)
            true_time = WindowsConnect(primary_dc, svc_act_un, svc_act_pwd, command)
            dc_datetime = FormatTime(dc_time)
            true_datetime = FormatTime(true_time)
            dc_ntp_status[dc] = GetOffset(dc_datetime, true_datetime)

        dc_ntp_console_out = []
        dc_ntp_drifts = []
        for k in dc_ntp_status:
            if 'GOOD' in dc_ntp_status[k][0]:
                dc_ntp_console_out.append(f'{k}: GOOD')
                dc_ntp_drifts.append(f'{k}: {dc_ntp_status[k][1]} seconds')
            else:
                dc_ntp_console_out.append(f'WARNING::{k} has drifted {dc_ntp_status[k][0]}')
                dc_ntp_drifts.append(f'{k}: {dc_ntp_status[k][1]} {dc_ntp_status[k][0]}')
        
        dc_ntp_sets = []
        for k in dc_ntp:
            servers = ', '.join(v for v in dc_ntp[k])
            dc_ntp_sets.append(f'{k}: {servers}')

        # get FW NTP settings and status
        fw_ntp = {}
        fw_ntp_status = {}
        for fw in vpc_fws:
            fw_ntp[fw] = []
            command = 'show sys ntp'
            fw_ntp_verbose = Exec(fw, netadmin_un, netadmin_pwd, command)
            fw_ntp_split = fw_ntp_verbose.splitlines()
            
            for idx, val in enumerate(fw_ntp_split):
                if 'set server' in val:
                    fw_ntp_server = val.split()
                    fw_ntp[fw].append(fw_ntp_server[2].strip('"'))

            command1 = 'get sys status'
            command2 = 'powershell.exe date'
            fw_ntp_status_verbose = Exec(fw, netadmin_un, netadmin_pwd, command1)
            true_time = WindowsConnect(primary_dc, svc_act_un, svc_act_pwd, command2)
            true_datetime = FormatTime(true_time)
            fw_ntp_status_split = fw_ntp_status_verbose.splitlines()

            for idx, val in enumerate(fw_ntp_status_split):
                if 'time' in val:
                    fw_time = val.split()
                    fw_time = ' '.join(fw_time[2:])
                    fw_datetime = FormatTime(fw_time)

            fw_ntp_status[fw] = GetOffset(fw_datetime, true_datetime)
        
        fw_ntp_console_out = []
        for k in fw_ntp_status:
            if 'GOOD' in fw_ntp_status[k][0]:
                fw_ntp_console_out.append(f'{k}: GOOD')
            else:
                fw_ntp_console_out.append(f'WARNING::{k} has drifted {fw_ntp_status[k][1]} {fw_ntp_status[k][0]}')

        fw_ntp_sets = []
        for k in fw_ntp:
            servers = ', '.join(v for v in fw_ntp[k])
            fw_ntp_sets.append(f'{k}: {servers}')

        # get LB NTP settings and status
        lb_ntp = {}
        lb_ntp_status = {}
        for lb in vpc_lbs:
            lb_ntp[lb] = []
            command = 'show running-config sys ntp'
            lb_ntp_verbose = Exec(lb, svc_act_un, svc_act_pwd, command)
            lb_ntp_split = lb_ntp_verbose.splitlines()
            
            for idx, val in enumerate(lb_ntp_split):
                if 'servers' in val:
                    lb_ntp_server = val.split()
            
            lb_ntp_server_list = []
            for val in lb_ntp_server:
                if 'servers' in val or '{' in val or '}' in val:
                    pass
                else:
                    lb_ntp[lb].append(val)

            command1 = 'show sys clock'
            command2 = 'powershell.exe date'
            lb_ntp_status_verbose = Exec(lb, netadmin_un, netadmin_pwd, command1)
            true_time = WindowsConnect(primary_dc, svc_act_un, svc_act_pwd, command2)
            true_datetime = FormatTime(true_time)
            lb_ntp_status_split = lb_ntp_status_verbose.splitlines()

            for idx, val in enumerate(lb_ntp_status_split):
                if ':' in val and 'Sys' not in val:
                    lb_time = val
                    lb_datetime = FormatTime(lb_time)

            lb_ntp_status[lb] = GetOffset(lb_datetime, true_datetime)

        lb_ntp_sets = []
        for k in lb_ntp:
            servers = ', '.join(v for v in lb_ntp[k])
            lb_ntp_sets.append(f'{k}: {servers}')

        lb_ntp_console_out = []
        for k in lb_ntp_status:
            if 'GOOD' in lb_ntp_status[k][0]:
                lb_ntp_console_out.append(f'{k}: GOOD')
            else:
                lb_ntp_console_out.append(f'WARNING::{k} has drifted {lb_ntp_status[k][1]} {lb_ntp_status[k][0]}')

        cr_tab = '\n\t\t\t   '
        print(f'''
        {vpc_name.upper()} 
            VPC DCHP-OPTIONS::
                DOMAIN   = {dn}
                DCS      = {', '.join(v for v in vpc_dc_ips)}
                NTP      = {', '.join(v for v in vpc_ntp_ips)}
            DC NTP::
                SETTINGS = {cr_tab.join(v for v in dc_ntp_sets)}
                STATUS   = {cr_tab.join(v for v in dc_ntp_console_out)}
                DRIFT    = {cr_tab.join(v for v in dc_ntp_drifts)}
            FW NTP::
                SETTINGS = {cr_tab.join(v for v in fw_ntp_sets)}
                STATUS   = {cr_tab.join(v for v in fw_ntp_console_out)}
            LB NTP::
                SETTINGS = {cr_tab.join(v for v in lb_ntp_sets)}
                STATUS   = {cr_tab.join(v for v in lb_ntp_console_out)}
        ''')
if True: # Exit script
    sys.exit()


