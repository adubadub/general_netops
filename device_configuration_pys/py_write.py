#! /usr/bin/env python3
if True: # Imports
    import sys
    import re
if True: # Define WRITE function (writes to py file)
    def WRITE(f, block, sec):
        if 'switch to' in block:
            f.write(f'\nif True: # {block}\n')
        else:
            f.write(f'\nif True: # {block} config\n')
        f.write("\tcommands = '''\n")
        for i in sec:
            f.write(f'\t{i}\n')
        f.write("\t'''\n")
        f.write('\tCONNECT()')
if True: # Define PARTITION function (finds current partition config)
    def PARTITION(conf_lines, partition_idxs, val):
        if val != partition_idxs[-1]:
            idx = partition_idxs.index(val)
            next_val = partition_idxs[idx + 1]
            partition = conf_lines[val:next_val + 1]
        else:
            partition = conf_lines[val:]
        return partition
if True: # Define SECTION function (finds current section config)
    def SECTION(partition, thissec, nextsec):
        this_sec = []
        next_sec = []
        for val in partition:
            if type(nextsec) == str:
                if thissec in val:
                    this_sec.append(partition.index(val))
                if nextsec in val and 'ecm' not in val:
                    next_sec.append(partition.index(val))
                    break
            else:
                if thissec in val:
                    this_sec.append(partition.index(val))
                    next_sec.append(-1)
                    break
        return partition[this_sec[0]:next_sec[0]]
if True: # Define OVERWRITE function (overwrites existing py for new config)
    def OVERWRITE_PY(dev):
        with open(f'{dev}.py', 'w+') as overwrite_file:
            overwrite_file.write('''if True: # Imports
    import os
    import paramiko
    import json\nif True: # Define CONNECT function (connect to device and add config)
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
if True: # Define CREATE_PY function (find applicable config and send to WRITE)
    def CREATE_PY(dev, conf_lines, part_loop, part_names, part_name_short):
        with open(f'{dev}.py', 'a+') as outfile:
            auth_section = SECTION(conf_lines, 'auth ', 'cli global')
            WRITE(outfile, 'auth', auth_section)

            if len(part_loop) == 0:
                cli_section = SECTION(conf_lines, 'cli global', 'cm ')
                WRITE(outfile, 'cli', cli_section)
                cm_section = SECTION(conf_lines, 'cm ', 'ltm ')
                WRITE(outfile, 'cm', cm_section)
            else:
                cli_section = SECTION(conf_lines, 'cli global', 'ltm ')
                WRITE(outfile, 'cli', cli_section)

            ltm_section = SECTION(conf_lines, 'ltm ', 'net ')
            WRITE(outfile, 'ltm', ltm_section)

            try:
                net_section = SECTION(conf_lines, 'net ', 'pem ')
                WRITE(outfile, 'net', net_section)
                pem_section = SECTION(conf_lines, 'pem ', 'security ')
                WRITE(outfile, 'pem', pem_section)
                security_section = SECTION(conf_lines, 'security ', 'sys a')
                WRITE(outfile, 'security', security_section)
            except:
                try:
                    net_section = SECTION(conf_lines, 'net ', 'security ')
                    WRITE(outfile, 'net', net_section)
                    security_section = SECTION(conf_lines, 'security ', 'sys a')
                    WRITE(outfile, 'security', security_section)    
                except:
                    net_section = SECTION(conf_lines, 'net ', 'sys a')
                    WRITE(outfile, 'net', net_section)                        

            sys_section = SECTION(conf_lines, 'sys a', 0)
            WRITE(outfile, 'sys', sys_section)
            
            if len(part_names) > 0:
                WRITE(outfile, f'switch to {part_name_short[0]} partition', [part_names[0]])
            
            part_loop.append('L')
            return len(part_loop)
if True: # Define BUILD function (parse backup file for config and send to CREATE_PY)
    def BUILD(conf_file):
        device = conf_file.split('.')
        device = device[0]
        OVERWRITE_PY(device)

        infile = open(f'config_files/{conf_file}', 'r+')
        raw = infile.read()
        comp_file = re.sub(r'(\n\s*)+\n', '\n', raw)
        comp_lines = comp_file.splitlines()
        infile.close()

        partition_names_raw = []
        partition_names = []
        partition_indices = []
        remove_indices = []

        for idx, val in enumerate(comp_lines):
            if 'cd /' in val:
                partition_indices.append(idx)
                partition_names_raw.append(val)
        for i, v in enumerate(partition_indices):
            if v == partition_indices[-1]:
                break
            else:
                diff = partition_indices[i + 1] - v
                if diff < 100:
                    remove_indices.append(i)

        partition_indices = [index for existing_index, index in enumerate(partition_indices) if existing_index not in remove_indices]
        partition_count = len(partition_indices)

        for val in partition_names_raw:
            new_val = val.split()
            for i, v in enumerate(new_val):
                if 'cd' in v:
                    part = new_val[i:]
                    cd_part = ','.join(part).replace(',', ' ').replace('/', '').replace('cd ', 'cd /')
                    if cd_part not in partition_names:
                        partition_names.append(cd_part)
        for val in partition_names:
            if 'Common' in val:
                partition_names.pop(partition_names.index(val))

        partition_name_short = []
        for v in partition_names:
            shortname = v.split()
            for val in shortname:
                if 'cd' in val:
                    shortname.pop(shortname.index(val))
                    partition_name_short.append(shortname[0])
        
        partition_loop = []
        loops = 0
        while loops < partition_count:
            current_partition = PARTITION(comp_lines, partition_indices, partition_indices[0])
            loops = CREATE_PY(device, current_partition, partition_loop, partition_names, partition_name_short)
            partition_indices.pop(0)
            if len(partition_name_short) > 0:
                partition_name_short.pop(0)
            if len(partition_names) > 0:
                partition_names.pop(0)