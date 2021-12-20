import paramiko

def Exec(addr, un, pwd, command):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(addr, port=22, username=un, password=pwd, look_for_keys=False, timeout=10)
    except:
        return 'NA'

    stdin, stdout, stderr = client.exec_command(command)
    output = (stdout.read()).decode("utf-8")
    
    stderr.close()
    stdout.close()
    stdin.close()
    client.close()
    return output

def Connect(addr, un, pwd, commands):
    pass