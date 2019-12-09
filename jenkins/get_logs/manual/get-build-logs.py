#! /usr/bin/env python3
if True: # Imports
    import sys
    import subprocess
    import json
    import time
    import paramiko
if True: # JSON variables
    with open('get-build-logs.json') as f:
        js = json.load(f)
        jenkins_un              = js['NETSVC_UN']
        jenkins_pwd             = js['NETSVC_PWD']
if True: # Local variables
    jenkins_ip              = '+JENKINS SERVER IP HERE+'
if True: # Define Connect function (Paramiko shell)
    def Connect(addr, un, pwd, command):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(addr, port=22, username=un, password=pwd, look_for_keys=False, timeout=10)
        remote_conn = client.invoke_shell()
        output = []

        remote_conn.send(f'{command}\n')
        time.sleep(.5)
        while True:
            if remote_conn.recv_ready():
                prompt = remote_conn.recv(9999)
                time.sleep(.5)
            else:
                break                
            prompt_str = prompt.decode("UTF-8")
            prompt_split = prompt_str.split()
            for i in prompt_split:
                output.append(i)
            continue
        
        remote_conn.close()
        client.close()
        return output
if True: # Define Exec function (Paramiko exec command)
    def Exec(addr, un, pwd, command):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(addr, port=22, username=un, password=pwd, look_for_keys=False, timeout=10)
        
        stdin, stdout, stderr = client.exec_command(command)
        output = (stdout.read()).decode("utf-8")
        
        stderr.close()
        stdout.close()
        stdin.close()
        client.close()
        return output
if True: # Define BuildNos function (gets build number indexes)
    def BuildNos(l):
        for i in l:
            if '*' in i:
                start_i = l.index(i)
        nos = l[start_i + 1:-2]
        return nos
if True: # Create log directory
    command = subprocess.Popen('mkdir jenkins_builds', stdout=subprocess.PIPE, shell=True)
    run = command.communicate()
if True: # Get job names
    cmd = r"cd /var/lib/jenkins/jobs/ && command printf '%s\n' *"
    jobs = Connect(jenkins_ip, jenkins_un, jenkins_pwd, cmd)

    for i, v in enumerate(jobs):
        if '*' in v:
            start_i = i
        if '[' in v:
            end_i = i

    job_list = jobs[start_i + 1:-2]
    job_build_dict = {}
if True: # Create job subdirectories
    for i in job_list:
        command = subprocess.Popen(f'mkdir jenkins_builds/{i.lower()}', stdout=subprocess.PIPE, shell=True)
        run = command.communicate()
        cmd = f"cd /var/lib/jenkins/jobs/{i}/builds/ && command printf '%s\\n' *"
        build_list = Connect(jenkins_ip, jenkins_un, jenkins_pwd, cmd)
        job_build_dict[i] = build_list
if True: # Get build numbers
    for key in job_build_dict:
        builds = BuildNos(job_build_dict[key])
        b_list = []
        for val in builds:
            if val.isnumeric():
                b_list.append(val)
        job_build_dict[key] = b_list
if True: # Create build subdirectories, get build log and write to local file
    for key in job_build_dict:
        for b in job_build_dict[key]:
            command = subprocess.Popen(f'mkdir jenkins_builds/{key}/{b}/', stdout=subprocess.PIPE, shell=True)
            run = command.communicate()
            cmd = f"cd /var/lib/jenkins/jobs/{key}/builds/{b}/ && command cat log"
            log = Exec(jenkins_ip, jenkins_un, jenkins_pwd, cmd)
            log_lines = log.splitlines()

            with open('log.txt', 'w+') as lf:
                for l in log_lines:
                    lf.write(f'{l}\n')
        
        command = subprocess.Popen(f'mv log.txt jenkins_builds/{key}/{b}/log.txt', stdout=subprocess.PIPE, shell=True)
        run = command.communicate()
if True: # Close script
    sys.exit()