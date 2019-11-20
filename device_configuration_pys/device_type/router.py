#! /usr/bin/env python3
if True: # Imports
    import sys
    import re
    import subprocess
if True: # Define functions
    def WRITE(f, block, sec):
        f.write(f'\nif True: # {block}\n')
        f.write("\tcommands = '''\n")
        f.write("\tconfigure terminal\n")
        f.write("\t!\n")
        if sec == 'MISSING':
            pass
        elif type(sec) == list:
            for i, v in enumerate(sec):
                if v == '!':
                    try:
                        if sec[i + 1] == '!':
                            pass
                        else:
                            f.write(f'\t{v}\n')
                    except:
                        f.write(f'\t{v}\n')
                else:
                    f.write(f'\t{v}\n')
        else:
            f.write(f'\t{sec}\n')
        f.write("\t!\n")
        f.write("\tend\n")
        f.write("\t!\n")
        f.write("\texit\n")
        f.write("\t'''\n")
        f.write('\tCONNECT()')

    def SECTION(config, thissec, nextsec):
        this_sec = []
        next_sec = []

        for idx, val in enumerate(config):
            if type(nextsec) == str:
                if 'access-list' in thissec and thissec in val.lower():
                    this_sec.append(config.index(val))
                elif f' {thissec}' in val.lower():
                    pass
                elif f'-{thissec}' in val.lower():
                    pass
                elif thissec in val.lower():
                    this_sec.append(config.index(val))
            else:
                if f' {thissec}' in val.lower():
                    pass
                elif f'-{thissec}' in val.lower():
                    pass
                elif thissec in val.lower():
                    if 'ip sla' in thissec:
                        this_sec.append(config[idx:idx + 3])
                    else:
                        this_sec.append(val)

        if type(nextsec) == str:
            try:
                sect = config[this_sec[0]:]
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

            hostname = SECTION(conf_lines, 'hostname', 0)
            WRITE(outfile, 'Hostname', hostname[0])
            boot_statement = SECTION(conf_lines, 'boot system', 0)
            WRITE(outfile, 'Boot Statement', boot_statement[0])
            trustpoint = SECTION(conf_lines, 'crypto pki trustpoint', '!')
            WRITE(outfile, 'Trustpoint', trustpoint)
            pvca2map = SECTION(conf_lines, 'crypto pki certificate map', 'crypto pki certificate chain')
            WRITE(outfile, 'pvca2map', pvca2map)
            domain_name = SECTION(conf_lines, 'ip domain name', 0)
            WRITE(outfile, 'IP Domain Name', domain_name)
            ip_hosts = SECTION(conf_lines, 'ip host', 0)
            WRITE(outfile, 'IP Host Entries', ip_hosts)
            track_statements = SECTION(conf_lines, 'track', 'crypto')
            WRITE(outfile, 'Track Statements', track_statements)                     
            key_chains = SECTION(conf_lines, 'key chain', '!')
            WRITE(outfile, 'Key Chains', key_chains)
            isakmp_policy = SECTION(conf_lines, 'crypto isakmp policy', 'crypto isakmp profile')
            isakmp_policy_new = []
            if 'MISSING' in isakmp_policy:
                isakmp_policy = SECTION(conf_lines, 'crypto isakmp policy', 'crypto ipsec')
            if 'MISSING' in isakmp_policy:
                isakmp_policy = SECTION(conf_lines, 'crypto isakmp', 'crypto ipsec')
            if 'MISSING' in isakmp_policy:
                isakmp_policy = '!'
            for v in isakmp_policy:
                if 'keepalive' not in v and 'key' not in v:
                    isakmp_policy_new.append(v)
            WRITE(outfile, 'ISAKMP Policy', isakmp_policy_new)
            isakmp_keys = SECTION(conf_lines, 'crypto isakmp key', 0)
            WRITE(outfile, 'ISAKMP Keys', isakmp_keys)
            isakmp_keepalives = SECTION(conf_lines, 'crypto isakmp keepalive', 0)
            WRITE(outfile, 'ISAKMP Keepalives', isakmp_keepalives)
            isakmp_profiles = SECTION(conf_lines, 'crypto isakmp profile', '!')
            WRITE(outfile, 'ISAKMP Profiles', isakmp_profiles)
            ikev2_prop = SECTION(conf_lines, 'crypto ikev2 proposal', '!')
            WRITE(outfile, 'IKEv2 Proposal', ikev2_prop)
            ikev2_policy = SECTION(conf_lines, 'crypto ikev2 policy', '!')
            WRITE(outfile, 'IKEv2 Policy', ikev2_policy)
            ikev2_keyring = SECTION(conf_lines, 'crypto ikev2 key', '!')
            WRITE(outfile, 'IKEv2 Keyring', ikev2_keyring)
            ikev2_profile = SECTION(conf_lines, 'crypto ikev2 profile', 'crypto ikev2 dpd')
            WRITE(outfile, 'IKEv2 Profile', ikev2_profile)
            ikev2_dpd = SECTION(conf_lines, 'crypto ikev2 dpd', 0)
            WRITE(outfile, 'IKEv2 Dead Peer Detection', ikev2_dpd)
            ikev2_frag = SECTION(conf_lines, 'crypto ikev2 frag', 0)
            WRITE(outfile, 'IKEv2 Fragmentation', ikev2_frag)
            crypto_keyring = SECTION(conf_lines, 'crypto keyring', '!')
            WRITE(outfile, 'Crypto Keyring', crypto_keyring)
            ipsec_life = SECTION(conf_lines, 'crypto ipsec security-association lifetime', 0)
            WRITE(outfile, 'IPSec Lifetimes', ipsec_life)
            ipsec_ts = SECTION(conf_lines, 'crypto ipsec transform', '!')
            WRITE(outfile, 'IPSec Transform Set', ipsec_ts)
            ipsec_profile = SECTION(conf_lines, 'crypto ipsec profile', 'crypto map')
            WRITE(outfile, 'IPSec Profile', ipsec_profile)
            crypto_map = SECTION(conf_lines, 'crypto map', '!')
            WRITE(outfile, 'Crypto Map', crypto_map)
            vti = SECTION(conf_lines, 'interface tunnel', 'interface gig')
            WRITE(outfile, 'VTI', vti)
            ints = SECTION(conf_lines, 'interface gig', 'forward-protocol')
            for i, v in enumerate(ints):
                if 'router' in v:
                    ints = ints[:i - 1]
            WRITE(outfile, 'Interfaces', ints)
            eigrp = SECTION(conf_lines, 'router eigrp', 'forward-protocol')
            for i, v in enumerate(eigrp):
                if 'nat' in v:
                    eigrp = eigrp[:i - 1]
                if 'router ospf' in v:
                    eigrp = eigrp[:i - 1]
            WRITE(outfile, 'EIGRP', eigrp)
            ospf = SECTION(conf_lines, 'router ospf', 'forward-protocol')
            for i, v in enumerate(ospf):
                if 'nat' in v:
                    ospf = ospf[:i - 1]
            WRITE(outfile, 'OSPF', ospf)
            nat = SECTION(conf_lines, 'ip nat', 0)
            WRITE(outfile, 'NAT Statements', nat)
            tftp = SECTION(conf_lines, 'ip tftp source-interface', 0)
            WRITE(outfile, 'TFTP', tftp)
            routes = SECTION(conf_lines, 'ip route', 0)
            WRITE(outfile, 'Routes', routes)
            sla = SECTION(conf_lines, 'ip sla', 0)
            sla_new = []
            if 'MISSING' in sla:
                sla_new.append('!')
            else:
                for v in sla:
                    for val in v:
                        if val not in sla_new:
                            sla_new.append(val)
            WRITE(outfile, 'SLAs', sla_new)
            prefixlists = SECTION(conf_lines, 'ip prefix-list', 0)
            WRITE(outfile, 'Prefix-Lists', prefixlists)
            accesslists = SECTION(conf_lines, 'access-list', 'control-plane')
            accesslists_new = []
            accesslists_final = []
            admin_list = 'NULL'
            for v in accesslists:
                if 'access-list' in v or 'permit' in v or 'deny' in v or '!' in v:
                    accesslists_new.append(v)
            for v in accesslists_new:
                if 'remark' in v.lower() and 'admin' in v.lower():
                    val = v.split()
                    for idx, nv in enumerate(val):
                        if 'access-list' in nv:
                            admin_list = str(' '.join(val[idx:idx + 2]))

                if admin_list in v.lower():
                    pass
                else:
                    accesslists_final.append(v)
            accesslists = list(set(accesslists_new) - set(accesslists_final))
            WRITE(outfile, 'ACLs', accesslists_final)
            routemaps = SECTION(conf_lines, 'route-map', '!')
            WRITE(outfile, 'Route-Maps', routemaps)
            crypto_logging = SECTION(conf_lines, 'crypto logging', 0)
            WRITE(outfile, 'Crypto Logging', crypto_logging)
            WRITE(outfile, 'Save Configuration', 'copy running-config startup-config')
            
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
            if 'show run' in val:
                config_start.append(idx)
            if '#' in val and 'exit' in val:
                config_end.append(idx)

        configuration = comp_lines[config_start[0]:config_end[0]]
        last_index = 0

        while last_index < config_end[0]:
            last_index = CREATE_PY(device, configuration, config_end[0])