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
                f.write(f'\tclish -c {v}\n')
        else:
            f.write(f'\tclish -c {sec}\n')
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

            exp_pwd = SECTION(conf_lines, 'set expert-password', 0)
            WRITE(outfile, 'Expert Password', exp_pwd)
            kernel_rts = SECTION(conf_lines, 'set kernel-routes', 0)
            WRITE(outfile, 'Kernel Routes', kernel_rts)
            mp_split = SECTION(conf_lines, 'set max-path-splits', 0)
            WRITE(outfile, 'Max Paths', mp_split)
            tracefile = SECTION(conf_lines, 'set tracefile', 0)
            WRITE(outfile, 'Tracefile', tracefile)
            syslog = SECTION(conf_lines, 'set syslog', 0)
            WRITE(outfile, 'Syslog', syslog)
            allowed_client = SECTION(conf_lines, 'allowed-client', 0)
            WRITE(outfile, 'Allowed Clients', allowed_client)
            edition = SECTION(conf_lines, 'set edition', 0)
            WRITE(outfile, 'Edition Settings', edition)
            core_dump = SECTION(conf_lines, 'core-dump', 0)
            WRITE(outfile, 'Core Dump Settings', core_dump)
            v6_state = SECTION(conf_lines, 'ipv6-state', 0)
            WRITE(outfile, 'IPv6 State', v6_state)
            dns = SECTION(conf_lines, 'set dns', 0)
            WRITE(outfile, 'DNS Settings', dns)
            domain_name = SECTION(conf_lines, 'set domainname', 0)
            WRITE(outfile, 'Domain Settings', domain_name)
            motd = SECTION(conf_lines, 'set message', 0)
            WRITE(outfile, 'Banner Config', motd)
            ntp = SECTION(conf_lines, 'set ntp', 0)
            WRITE(outfile, 'NTP Settings', ntp)
            installer = SECTION(conf_lines, 'set installer', 0)
            WRITE(outfile, 'Installer Policy', installer)
            lcd = SECTION(conf_lines, 'set lcd', 0)
            WRITE(outfile, 'LCD Settings', lcd)
            clienv = SECTION(conf_lines, 'set clienv', 0)
            WRITE(outfile, 'CLI Settings', clienv)
            webui = SECTION(conf_lines, 'set web ', 0)
            WRITE(outfile, 'WebUI Settings', webui)
            pwd_ctrl = SECTION(conf_lines, 'set password-controls', 0)
            WRITE(outfile, 'Password Control Settings', pwd_ctrl)
            email = SECTION(conf_lines, 'set mail-notification ', 0)
            WRITE(outfile, 'EMail Notification Settings', email)
            cron = SECTION(conf_lines, 'add cron', 0)
            WRITE(outfile, 'CRON Jobs', cron)
            backups = SECTION(conf_lines, 'backup-scheduled', 0)
            WRITE(outfile, 'Backup Settings', backups)
            snmp = SECTION(conf_lines, 'set snmp ', 0)
            WRITE(outfile, 'SNMP Settings', snmp)
            ints = SECTION(conf_lines, 'set interface ', 0)
            WRITE(outfile, 'Interface Config', ints)
            rip = SECTION(conf_lines, 'set rip ', 0)
            WRITE(outfile, 'RIP Config', rip)
            mgmt_int = SECTION(conf_lines, 'set management ', 0)
            WRITE(outfile, 'Management Interface Settings', mgmt_int)
            tz = SECTION(conf_lines, 'set timezone ', 0)
            WRITE(outfile, 'Timezone Settings', tz)
            hostname = SECTION(conf_lines, 'set hostname ', 0)
            WRITE(outfile, 'Hostname Config', hostname)
            timeout = SECTION(conf_lines, 'inactivity', 0)
            WRITE(outfile, 'Idle Timeout Settings', timeout)
            routes = SECTION(conf_lines, 'set static-route', 0)
            WRITE(outfile, 'Static Routes', routes)
            aaa = SECTION(conf_lines, 'set aaa', 0)
            WRITE(outfile, 'AAA Config', aaa)
            local_users = SECTION(conf_lines, 'set user', 0)
            WRITE(outfile, 'Local User Accounts', local_users)
            rba_users = SECTION(conf_lines, 'rba user', 0)
            WRITE(outfile, 'RBA User Accounts', rba_users)
            format_global = SECTION(conf_lines, 'set format', 0)
            WRITE(outfile, 'Global Format Settings', format_global)
            net_access = SECTION(conf_lines, 'set net-access', 0)
            WRITE(outfile, 'Network Access Settings', net_access)
            ospf = SECTION(conf_lines, 'set ospf', 0)
            WRITE(outfile, 'OSPF Config', ospf)
            arp = SECTION(conf_lines, 'set arp', 0)
            WRITE(outfile, 'ARP Settings', arp)
            arppxy = SECTION(conf_lines, 'arp proxy', 0)
            WRITE(outfile, 'ARP Proxy Settings', arppxy)
            host_entries = SECTION(conf_lines, 'host name', 0)
            WRITE(outfile, 'Host Entries', host_entries)
            add_cmd = SECTION(conf_lines, 'add command', 0)
            WRITE(outfile, 'Added Commands', add_cmd)

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
            if '#' in val and '"show configuration"' in val:
                config_start.append(idx)
            if '#' in val and 'route -n' in val:
                config_end.append(idx)

        configuration = comp_lines[config_start[0]:config_end[0]]
        last_index = 0

        while last_index < config_end[0]:
            last_index = CREATE_PY(device, configuration, config_end[0])