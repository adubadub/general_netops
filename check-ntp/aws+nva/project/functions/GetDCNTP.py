from functions.WindowsConnect import ExecCmd
from functions.FormatTime import StringtoDT
from functions.GetTimeDelta import GetTD

def Time(servers, un, pwd):
    command = 'powershell.exe date'
    true_time = 'NA'
    for dc in servers:
        try:
            true_time = ExecCmd(dc, un, pwd, command)
            if true_time != 'NA':
                break
        except:
            continue

    if true_time == 'NA':
        return 'NA'
    else:    
        dt = StringtoDT(true_time)
        return dt

def Settings(dc, un, pwd, info):
    ntp_servers = []
    ntp_configuration = []
    ntp_source = []
    if 'peers' in info.lower():
        command = 'w32tm /query /peers'        
        ntp_settings_verbose = ExecCmd(dc, un, pwd, command)
        ntp_settings_split = ntp_settings_verbose.split()
        for idx, val in enumerate(ntp_settings_split):
            if 'Peer:' in val:
                server = ntp_settings_split[idx + 1]
                try:
                    server_split = server.split(',')
                    server = server_split[0]
                    ntp_servers.append(server)
                except:
                    ntp_servers.append(server)
        return ntp_servers
    if 'configuration' in info.lower():
        command = 'w32tm /query /configuration'        
        ntp_settings_verbose = ExecCmd(dc, un, pwd, command)
        ntp_settings_split = ntp_settings_verbose.splitlines()
        for l in ntp_settings_split:
            ntp_configuration.append(l)
        return ntp_configuration
    if 'source' in info.lower():
        command = 'w32tm /query /source'        
        ntp_settings_verbose = ExecCmd(dc, un, pwd, command)
        ntp_source.append(ntp_settings_verbose)
        return ntp_configuration
    else:
        return 'Error: Need paramater (peers, configuration, or source)'

def Delta(dc, source_dc, un, pwd):
    command = 'powershell.exe date'
    dc_time = ExecCmd(dc, un, pwd, command)
    true_time = 'NA'
    loop = 0
    while loop < len(source_dc):
        for dc in source_dc:
            try:
                true_time = ExecCmd(source_dc, un, pwd, command)
                if true_time != 'NA':
                    break
            except:
                loop = loop + 1
                
    if true_time == 'NA':
        return 'NA'
    else:    
        dc_datetime = StringtoDT(dc_time)
        true_datetime = StringtoDT(true_time)
        dc_ntp_delta = GetTD(dc_datetime, true_datetime)
        return dc_ntp_delta