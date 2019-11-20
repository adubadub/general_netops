#! /usr/bin/env python3
if True: # Imports
    import sys
    import re
    import subprocess
if True: # Define functions
    def WRITE(f, block, sec):
        f.write(f'\nif True: # {block}\n')
        f.write("\tcommands = '''\n")
        f.write("\t#\n")
        if sec == 'MISSING':
            pass
        elif type(sec) == list:
            for v in sec:
                if 'set uuid' in v:
                    pass
                else:
                    f.write(f'\t{v}\n')
        else:
            f.write(f'\t{sec}\n')
        f.write("\t#\n")
        f.write("\t'''\n")
        f.write('\tCONNECT()')

    def SECTION(config, thissec, nextsec):
        this_sec = []
        next_sec = []

        for val in config:
            if type(nextsec) == str:
                if thissec in val.lower():
                    this_sec.append(config.index(val))
            else:
                if thissec in val.lower():  
                    this_sec.append(val)

        if type(nextsec) == str:
            try:
                sect = config[this_sec[0]:]
                if nextsec == 'done':
                    return sect
                else:
                    for val in sect:
                        if nextsec in val.lower():
                            next_sec.append(sect.index(val))
                return sect[0:next_sec[0]]
            except IndexError:
                return 'MISSING'
        else:
            if len(this_sec) > 0:
                return this_sec
            else:
                return 'MISSING'

    def OVERWRITE_PY(dev):
        with open(f'{dev}.py', 'w+') as overwrite_file:
            overwrite_file.write('''if True: # Imports
    import os
    import paramiko
    import json\nif True: # Define CONNECT function (connect to device)
    def CONNECT():
    \tip_addr = os.environ['IP']
    \tusername = os.environ['USERNAME']
    \tpassword = os.environ['PASSWORD']
    \tclient = paramiko.SSHClient()
    \tclient.load_system_host_keys()
    \tclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    \tclient.connect(ip_addr, '22', username, password, look_for_keys=False, timeout=5)
    \tstdin, stdout, stderr = client.exec_command(commands)
    \toutput = stdout.read()
    \texit_status = stdout.channel.recv_exit_status()
    \tif exit_status == 0:
    \t\tprint(output)
    \t\tstdout.close()
    \t\tstdin.close()
    \t\tclient.close()
    \telse:
    \t\tprint('Error')'''
    )

    def CREATE_PY(dev, conf_lines, last_idx):
        with open(f'{dev}.py', 'a+') as outfile:

            version = SECTION(conf_lines, 'config-version', 0)
            WRITE(outfile, 'Version', version[0])
            conf_file = SECTION(conf_lines, 'conf_file', 0)
            WRITE(outfile, 'Config File', conf_file[0])
            buildno = SECTION(conf_lines, 'buildno', 0)
            WRITE(outfile, 'Build Number', buildno[0])
            globalvdoms = SECTION(conf_lines, 'global_vdom', 0)
            WRITE(outfile, 'Global VDOM Count', globalvdoms[0])
            sysconf = SECTION(conf_lines, 'config system', 'config user')
            WRITE(outfile, 'System Config', sysconf)
            device_cat = SECTION(conf_lines, 'config user', 'config system cluster')
            WRITE(outfile, 'Device Categories', device_cat)  
            cluster_sync = SECTION(conf_lines, ' cluster-sync', ' fortiguard')
            WRITE(outfile, 'Cluster Sync', cluster_sync) 
            ips = SECTION(conf_lines, 'config ips', 'config log')
            WRITE(outfile, 'IPS Global Settings', ips)
            syslogs = SECTION(conf_lines, 'config log', ' email-server')
            WRITE(outfile, 'Syslog', syslogs)
            emailer = SECTION(conf_lines, ' email-server', ' session-helper')
            WRITE(outfile, 'EMail Settings', emailer)
            session_help = SECTION(conf_lines, ' session-helper', ' console')
            WRITE(outfile, 'Session Helpers', session_help)
            console = SECTION(conf_lines, ' console', ' ntp')
            WRITE(outfile, 'Console Settings', console)
            ntp = SECTION(conf_lines, ' ntp', 'config system settings')
            WRITE(outfile, 'NTP Settings', ntp)
            global_sets = SECTION(conf_lines, 'config system settings', 'config system zone')
            WRITE(outfile, 'Global Settings', global_sets)
            zones = SECTION(conf_lines, 'config system zone', 'config firewall')
            WRITE(outfile, 'Zones', zones)
            v4addr_objects = SECTION(conf_lines, 'config firewall address', ' multicast-address')
            WRITE(outfile, 'IPv4 Address Objects', v4addr_objects)
            v6addr_objects = SECTION(conf_lines, 'config firewall address6', ' multicast-address6')
            WRITE(outfile, 'IPv6 Address Objects', v6addr_objects)
            v4mcast_objects = SECTION(conf_lines, ' multicast-address', ' firewall address6')
            WRITE(outfile, 'IPv4 Multicast Address Objects', v4mcast_objects)
            v6mcast_objects = SECTION(conf_lines, ' multicast-address6', ' addrgrp')
            WRITE(outfile, 'IPv6 Multicast Address Objects', v6mcast_objects)
            addrgrp = SECTION(conf_lines, 'config firewall addrgrp', 'config firewall service')
            WRITE(outfile, 'Address Groups', addrgrp)
            service_cats = SECTION(conf_lines, 'config firewall service category', ' service custom')
            WRITE(outfile, 'Service Categories', service_cats)
            services = SECTION(conf_lines, ' service custom', ' service group')
            WRITE(outfile, 'Service Objects', services)
            svcgrp = SECTION(conf_lines, ' service group', 'config webfilter ')
            WRITE(outfile, 'Service Groups', svcgrp)
            webfilter = SECTION(conf_lines, 'config webfilter ', 'config ips ')
            WRITE(outfile, 'Web Filters', webfilter)
            ips_sensor = SECTION(conf_lines, 'config ips sensor', 'config web-proxy ')
            WRITE(outfile, 'IPS Sensors', ips_sensor)
            webproxy = SECTION(conf_lines, 'config web-proxy ', 'config application ')
            WRITE(outfile, 'Web Proxies', webproxy)
            applist = SECTION(conf_lines, 'config application ', 'config dlp ')
            WRITE(outfile, 'Application Lists', applist)
            dlp_sensor = SECTION(conf_lines, 'config dlp sensor', 'config webfilter ')
            WRITE(outfile, 'DLP Sensors', dlp_sensor)
            urlfilter = SECTION(conf_lines, ' webfilter urlfilter', ' threat-weight')
            WRITE(outfile, 'Whitelists', urlfilter)
            log_weights = SECTION(conf_lines, ' threat-weight', 'config icap profile')
            WRITE(outfile, 'Log Threat-Weights', log_weights)
            icap = SECTION(conf_lines, 'config icap profile', 'config vpn ')
            WRITE(outfile, 'iCAP Profile', icap)
            certs_ca = SECTION(conf_lines, 'config vpn certificate ca', 'config vpn certificate local')
            WRITE(outfile, 'CA Certificates', certs_ca)
            certs_local = SECTION(conf_lines, 'config vpn certificate local', 'config user ')
            WRITE(outfile, 'Local Certificates', certs_local)
            user_sets = SECTION(conf_lines, ' user setting', ' user peer')
            WRITE(outfile, 'User Settings', user_sets)
            user_peer = SECTION(conf_lines, ' user peer', ' user group')
            WRITE(outfile, 'User Peers', user_peer)
            user_grp = SECTION(conf_lines, ' user group', 'config vpn ssl ')
            WRITE(outfile, 'User Groups', user_grp)
            sslvpn_hc = SECTION(conf_lines, 'config vpn ssl ', 'config vpn ssl settings')
            WRITE(outfile, 'SSL VPN Host Check Settings', sslvpn_hc)
            sslvpn_sets = SECTION(conf_lines, 'config vpn ssl settings', 'config voip')
            WRITE(outfile, 'SSL VPN Settings', sslvpn_sets)
            voip_profile = SECTION(conf_lines, 'config voip', 'config webfilter profile')
            WRITE(outfile, 'VoIP Profiles', voip_profile)
            wf_profile = SECTION(conf_lines, 'config webfilter profile', 'config webfilter search-engine')
            WRITE(outfile, 'Web Filter Profiles', wf_profile)
            wf_se = SECTION(conf_lines, 'config webfilter search-engine', 'config vpn ipsec ')
            WRITE(outfile, 'Web Filter Search Engine Setttings', wf_se)
            ipsec_p1 = SECTION(conf_lines, 'config vpn ipsec phase1-interface', 'config vpn ipsec phase2-interface')
            WRITE(outfile, 'IPSEC Phase1', ipsec_p1)
            ipsec_p2 = SECTION(conf_lines, 'config vpn ipsec phase2-interface', 'config antivirus ')
            WRITE(outfile, 'IPSEC Phase2', ipsec_p2)
            antivirus_sets = SECTION(conf_lines, 'config antivirus ', 'config antivirus profile')
            WRITE(outfile, 'Anti-Virus Settings', antivirus_sets)
            antivirus_profile = SECTION(conf_lines, 'config antivirus profile', 'config spamfilter ')
            WRITE(outfile, 'Anti-Virus Profiles', antivirus_profile)
            spamfilter_profile = SECTION(conf_lines, 'config spamfilter ', 'config wanopt ')
            WRITE(outfile, 'Spam Filter Profiles', spamfilter_profile)
            wanopt_sets = SECTION(conf_lines, 'config wanopt settings', 'config wanopt profile')
            WRITE(outfile, 'WAN Optimization Settings', wanopt_sets)
            wanopt_profile = SECTION(conf_lines, 'config wanopt profile', 'config firewall ')
            WRITE(outfile, 'WAN Optimization Profiles', wanopt_profile)
            fw_skeds = SECTION(conf_lines, 'config firewall schedule ', 'config firewall profile-protocol-options')
            WRITE(outfile, 'Firewall Schedules', fw_skeds)
            fw_ppo = SECTION(conf_lines, 'config firewall profile-protocol-options', ' ssl-ssh-profile')
            WRITE(outfile, 'Firewall Profile Protocol Options', fw_ppo)
            fw_sslssh = SECTION(conf_lines, ' ssl-ssh-profile', 'config waf ')
            WRITE(outfile, 'Firewall SSL/SSH Profiles', fw_sslssh)
            fw_waf = SECTION(conf_lines, 'config waf ', 'config firewall profile-group')
            WRITE(outfile, 'Firewall WAF Profiles', fw_waf)
            fw_profgrp = SECTION(conf_lines, 'config firewall profile-group', 'config firewall policy')
            WRITE(outfile, 'Firewall Profile Groups', fw_profgrp)
            fw_policy = SECTION(conf_lines, 'config firewall policy', 'config firewall proxy-policy')
            WRITE(outfile, 'Firewall Policy', fw_policy)
            fw_pxypol = SECTION(conf_lines, 'config firewall proxy-policy', 'config switch-controller ')
            WRITE(outfile, 'Firewall Proxy Policy', fw_pxypol)
            switch_cont = SECTION(conf_lines, 'config switch-controller ', 'config endpoint-control ')
            WRITE(outfile, 'Switch Settings', switch_cont)
            ep_cont = SECTION(conf_lines, 'config endpoint-control ', 'config wireless-controller wids-profile')
            WRITE(outfile, 'EndPoint-Control Settings', ep_cont)
            wlc_wids = SECTION(conf_lines, 'config wireless-controller wids-profile', ' wtp-profile')
            WRITE(outfile, 'WLC WIDS Profile', wlc_wids)
            wlc_wtp = SECTION(conf_lines, ' wtp-profile', 'config log ')
            WRITE(outfile, 'WLC WIDS Profile', wlc_wtp)
            log_config = SECTION(conf_lines, 'config log memory ', 'config router ')
            WRITE(outfile, 'Log Settings', log_config)
            rip = SECTION(conf_lines, 'config router rip', 'config router static')
            WRITE(outfile, 'RIP/RIPNG Config', rip)
            static = SECTION(conf_lines, 'config router static', 'config router ospf')
            WRITE(outfile, 'Static Route Config', static)
            ospf = SECTION(conf_lines, 'config router ospf', 'config router bgp')
            WRITE(outfile, 'OSPF/OSPF6 Config', ospf)
            bgp = SECTION(conf_lines, 'config router bgp', 'config router isis')
            WRITE(outfile, 'BGP Config', bgp)
            isis = SECTION(conf_lines, 'config router isis', 'config router multicast')
            WRITE(outfile, 'ISIS Config', isis)
            mcast = SECTION(conf_lines, 'config router multicast', 'done')
            WRITE(outfile, 'Multicast Routing Config', mcast)

            return last_idx + 1

    def BUILD(conf_file):
        device = conf_file.split('.')
        device = device[0]
        OVERWRITE_PY(device)

        infile = open(f'config_files/{conf_file}', 'r+')
        raw = infile.read()
        comp_file = re.sub(r'(\n\s*)+\n', '\n', raw)
        comp_lines = comp_file.splitlines()
        infile.close()

        config_start = []
        config_end = []

        for idx, val in enumerate(comp_lines):
            if 'show' in val:
                config_start.append(idx)
            if '#' in val and 'exit' in val:
                config_end.append(idx)

        configuration = comp_lines[config_start[0]:config_end[0]]
        last_index = 0

        while last_index < config_end[0]:
            last_index = CREATE_PY(device, configuration, config_end[0])