#! /usr/bin/env python3
if True: # imports
    import json
    import sys
if True: # function imports
    from functions import GetAWSDHCPSets
    from functions import GetDCNTPState
    from functions import SendCommands
    from functions import ConvertTimeDelta
    from functions import FormatTime
    from functions import GetTimeDelta
    from functions import ConvertTimeDelta
if True: # set env variables
    with open('aws+nva_ntp-check_project.json') as f:
        js              = json.load(f)
        device_dict     = js['VPCS']
        svc_act_un      = js['SVC_UN']
        svc_act_pwd     = js['SVC_PWD']
        netadmin_un     = js['NETADMIN_UN']
        netadmin_pwd    = js['NETADMIN_PWD']
if True: # Code
    for vpc in device_dict:
        # set working variables
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
        dn = GetAWSDHCPSets.Get(vpc_name, awscreds, 'domain')
        vpc_dc_ips = GetAWSDHCPSets.Get(vpc_name, awscreds, 'dcs')
        vpc_ntp_ips = GetAWSDHCPSets.Get(vpc_name, awscreds, 'ntp')

        # get DC NTP status and drift
        dc_ntp = {}
        dc_ntp_status = {}
        dc_ntp_drift = {}
        dc_ntp_sets = []
        dc_ntp_console_out = []
        dc_ntp_drifts = []
        for dc in vpc_dcs:
            dc_ntp[dc] = GetDCNTPState.Settings(dc, svc_act_un, svc_act_pwd, 'peers')
            if 'Error:' in dc_ntp[dc]:
                dc_ntp_sets.append(f'{dc}: {str(dc_ntp[dc])}')
            else:    
                servers = ', '.join(v for v in dc_ntp[dc])
                dc_ntp_sets.append(f'{dc}: {dc_ntp[dc][0]}')
            
            dc_ntp_delta = GetDCNTPState.Delta(dc, dc_ntp[dc], svc_act_un, svc_act_pwd)

            if dc_ntp_delta != 'NA':
                dc_ntp_status[dc], dc_ntp_drift[dc] = ConvertTimeDelta.ConvertTD(dc_ntp_delta)
            else:
                dc_ntp_status[dc], dc_ntp_drift[dc] = 'Error: Could not connect to NTP source', 'NA'

            if 'GOOD' in dc_ntp_status[dc][0]:
                dc_ntp_console_out.append(f'{dc}: {dc_ntp_status[dc][0]}')
                dc_ntp_drifts.append(f'{dc}: {dc_ntp_drift[dc][0]} seconds')
            if 'NA' in dc_ntp_delta:
                dc_ntp_console_out.append(f'{dc}: {dc_ntp_status[dc]}')
                dc_ntp_drifts.append(f'{dc}: NA: Could not connect to NTP source')
            else:
                dc_ntp_console_out.append(f'WARNING::{dc} has drifted {dc_ntp_status[dc][0]}')
                dc_ntp_drifts.append(f'{dc}: {dc_ntp_drift[dc][0]} {dc_ntp_status[dc][0]}')
        
        # get FW NTP settings and status
        fw_ntp = {}
        fw_ntp_status = {}
        fw_ntp_sets = []
        fw_ntp_console_out = []
        err_msg = 'Error: Could not connect'
        for fw in vpc_fws:
            fw_ntp[fw] = []
            command = 'show sys ntp'
            fw_ntp_verbose = SendCommands.Exec(fw, netadmin_un, netadmin_pwd, command)
            
            if fw_ntp_verbose != 'NA':
                fw_ntp_split = fw_ntp_verbose.splitlines()

                for idx, val in enumerate(fw_ntp_split):
                    if 'set server' in val:
                        fw_ntp_server = val.split()
                        fw_ntp[fw].append(fw_ntp_server[2].strip('"'))
                servers = ', '.join(v for v in fw_ntp[fw])
                fw_ntp_sets.append(f'{fw}: {servers}')

                command = 'get sys status'
                fw_ntp_status_verbose = SendCommands.Exec(fw, netadmin_un, netadmin_pwd, command)
                true_datetime = GetDCNTPState.Time(fw_ntp[fw], svc_act_un, svc_act_pwd)
                fw_ntp_status_split = fw_ntp_status_verbose.splitlines()

                for idx, val in enumerate(fw_ntp_status_split):
                    if 'time' in val:
                        fw_time = val.split()
                        fw_time = ' '.join(fw_time[2:])
                        fw_datetime = FormatTime.StringtoDT(fw_time)

                if true_datetime != 'NA':
                    fw_ntp_delta = GetTimeDelta.GetTD(fw_datetime, true_datetime)
                    fw_ntp_status[fw] = ConvertTimeDelta.ConvertTD(fw_ntp_delta)
                else:
                    fw_ntp_status[fw] = 'Error: Could not connect to NTP source'
            else:
                fw_ntp[fw] = err_msg
                fw_ntp_sets.append(f'{fw}: {err_msg}')
                fw_ntp_status[fw] = 'NA'
                true_datetime = 'Pass'
            
            if 'GOOD' in fw_ntp_status[fw][0]:
                fw_ntp_console_out.append(f'{fw}: GOOD')
            elif 'Error:' in fw_ntp[fw]:
                fw_ntp_console_out.append(f'{fw}: {fw_ntp[fw]}')
            elif true_datetime == 'NA':
                fw_ntp_console_out.append(f'{fw}: {fw_ntp_status[fw]}')
            else:
                fw_ntp_console_out.append(f'WARNING::{fw} has drifted {str(fw_ntp_status[fw][1])} {str(fw_ntp_status[fw][0])}')

        # get LB NTP settings and status
        lb_ntp = {}
        lb_ntp_status = {}
        lb_ntp_sets = []
        lb_ntp_console_out = []
        err_msg = 'Error: Could not connect'
        for lb in vpc_lbs:
            lb_ntp[lb] = []
            command = 'show running-config sys ntp'
            lb_ntp_verbose = SendCommands.Exec(lb, svc_act_un, svc_act_pwd, command)
            
            if lb_ntp_verbose != 'NA':
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
                servers = ', '.join(v for v in lb_ntp[lb])
                lb_ntp_sets.append(f'{lb}: {servers}')

                command = 'show sys clock'
                lb_ntp_status_verbose = SendCommands.Exec(lb, svc_act_un, svc_act_pwd, command)
                true_datetime = GetDCNTPState.Time(lb_ntp[lb], svc_act_un, svc_act_pwd)
                lb_ntp_status_split = lb_ntp_status_verbose.splitlines()

                for idx, val in enumerate(lb_ntp_status_split):
                    if ':' in val and 'Sys' not in val:
                        lb_time = val
                        lb_datetime = FormatTime.StringtoDT(lb_time)

                if true_datetime != 'NA':
                    lb_ntp_delta = GetTimeDelta.GetTD(lb_datetime, true_datetime)
                    lb_ntp_status[lb] = ConvertTimeDelta.ConvertTD(lb_ntp_delta)
                else:
                    lb_ntp_status[lb] = 'Error: Could not connect to NTP source'
            else:
                lb_ntp[lb] = err_msg
                lb_ntp_sets.append(f'{lb}: {err_msg}')
                lb_ntp_status[lb] = 'NA'
                true_datetime = 'Pass'
            
            if 'GOOD' in lb_ntp_status[lb][0]:
                lb_ntp_console_out.append(f'{lb}: GOOD')
            elif 'Error:' in lb_ntp[lb]:
                lb_ntp_console_out.append(f'{lb}: {lb_ntp[lb]}')
            elif true_datetime == 'NA':
                lb_ntp_console_out.append(f'{lb}: {lb_ntp_status[lb]}')
            else:
                lb_ntp_console_out.append(f'WARNING::{lb} has drifted {str(lb_ntp_status[lb][1])} {str(lb_ntp_status[lb][0])}')

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