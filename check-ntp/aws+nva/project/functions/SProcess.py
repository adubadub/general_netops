import subprocess

def Command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0].strip()
    return output

def Interactive(command):
    pass