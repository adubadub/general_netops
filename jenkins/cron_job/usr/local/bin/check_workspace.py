#! /usr/bin/env python3
import sys
import subprocess
import json

job_output = subprocess.getoutput('cd /var/lib/jenkins/jobs/ && ls')
job_split = job_output.split()

job_last = subprocess.getoutput('cat job_list.txt')
job_last_split = job_last.splitlines()
job_list = job_last_split

for j in job_split:
    if j in job_last_split:
        pass
    else:
        job_list.append(j)
        command = subprocess.Popen(f'echo {j} >> job_list.txt', stdout=subprocess.PIPE, shell=True)
        command.communicate()

with open('check_workspace.json') as f:
    js = json.load(f)
    job_dict_last = js['LAST_BUILDS']

job_dict_new = {}
for j in job_list:
    files = subprocess.getoutput(f'cd /var/lib/jenkins/jobs/{j}/builds/ && ls -l')
    files_split = files.split()

    build_nos = []
    for i, f in enumerate(files_split):
        if 'dr' in f:
            build_nos.append(files_split[i + 8])
            job_dict_new[j] = build_nos

new_builds = {}
for k in job_dict_new:
    try:
        job_dict_last[k]
    except:
        bno = [job_dict_new[k]]
        job_dict_last[k] = bno

command = subprocess.Popen(f'echo > check_workspace.json', stdout=subprocess.PIPE, shell=True)
command.communicate()
with open('check_workspace.json', 'r+') as nf:
    for k in job_dict_new:
        try:
            buildno = job_dict_new[k][-1]
            if buildno in job_dict_last[k]:
                pass
            else:
                new_builds[k] = [buildno]
                js['LAST_BUILDS'][k] = [buildno]
        except:
            pass
    
    json.dump(js, nf)

to_log = {}
for k in new_builds:
    to_log[k] = [new_builds[k]]
    console = subprocess.getoutput(f'cd /var/lib/jenkins/jobs/{k}/builds/{new_builds[k]}/ && cat log')
    console_split = console.splitlines()

    for l in console_split:
        try:
            if 'started by' in l.lower():
                if 'user' in l.lower():
                    l = l.split('[0m')
                    l = l[1]
                    to_log[k].append(str(l))
                else:
                    to_log[k].append(str(l))
            elif 'finished:' in l.lower():
                to_log[k].append(l)
        except:
            to_log[k].append('unknown user')
            to_log[k].append('unknown result')

for k in new_builds:
    try:
        no = new_builds[k]
        build = no[-1]
        job_log = subprocess.getoutput(f'cd /var/log/jenkins/ && cat jenkins.log | grep Run#execute:.{k}.#{build}')
        job_log_split = job_log.split()   
        job_date = job_log_split[0]
        job_time = job_log_split[1]
        d_time = f'{job_date} {job_time}'
        to_log[k].append(d_time)
    except:
        to_log[k].append('null')

for k in to_log:
    try:
        build_dict = to_log[k]
        command = f'echo "{build_dict[3]} EXECUTED_BUILD {k} #{build_dict[0]} BY {build_dict[1]} WAS {build_dict[2]}" >> /var/log/jenkins/jenkins_custom.log'
        wr = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        wr.communicate()
    except:
        build_dict = to_log[k]
        command = f'echo "unknown time EXECUTED_BUILD {k} #{build_dict[0]} BY unknown user WAS unknown result" >> /var/log/jenkins/jenkins_custom.log'
        wr = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        wr.communicate()

sys.exit()