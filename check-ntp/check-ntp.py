#! /usr/bin/env python3
if True: # imports
    import sys
    import json
    import pypsrp
    from pypsrp.client import Client
if True: # set env variables
    with open('check-ntp.json') as f:
        js              = json.load(f)
        dc_dict         = js['ENVIRONMENT']
        svc_act_un      = js['SVC_UN']
        svc_act_pwd     = js['SVC_PWD']
        user            = js['DOMAIN_UN']
        pwd             = js['DOMAIN_PWD']
if True: # define get datetime functions
    def GetTime(dc):
        dc_client = Client(dc, username=svc_act_un,
            password=svc_act_pwd,
            cert_validation=False,
            ssl=False
            )

        dc_time = dc_client.execute_cmd('powershell.exe date')
        dc_time = dc_time[0].strip()
        return dc_time
if True: # get date and time difference between NTP SOURCE DC and NTP CLIENT DC with pypsrp client
    for env in dc_dict:
        dc_list = []
        ntp_source_dc = dc_dict[env][0]
        for dc in dc_dict[env][1:]:
            dc_list.append(dc)

        for dc in dc_list:
            dc_datetime = GetTime(dc)
            true_datetime = GetTime(ntp_source_dc)
            dc_dt_split = dc_datetime.split()
            t_dt_split = true_datetime.split()
            
            if dc_dt_split[0:4] == t_dt_split[0:4]:
                dc_time_split = dc_dt_split[4].split(':')
                truth_time_split = t_dt_split[4].split(':')
                if dc_time_split[0:2] == truth_time_split[0:2]:
                    dc_sec = int(dc_time_split[2])
                    truth_sec = int(truth_time_split[2])
                    drift = truth_sec - dc_sec
                    if drift > 2:
                        print(f'WARNING:: {env}:{dc} NTP has drifted {drift} seconds from MVPC!')
                    else:
                        print(f'{env}:{dc} NTP is GOOD')
                else:
                    print(f'WARNING:: {env}:{dc} NTP has drifted by minutes/hours!')
            else:
                print(f'WARNING:: {env}:{dc} NTP has drifted by days/years!')
if True: # Exit script
    sys.exit()


