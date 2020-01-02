import pypsrp
from pypsrp.client import Client

def ExecCmd(dc, un, pwd, commands):
    dc_client = Client(dc, username=un,
        password=pwd,
        cert_validation=False,
        ssl=False
        )
    output = dc_client.execute_cmd(commands)
    output = output[0].strip()
    return output