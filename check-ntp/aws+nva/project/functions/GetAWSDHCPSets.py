from functions.SProcess import Command

def Get(vpc_name, aws_creds, info):
    dc_ips = []
    ntp_ips = []
    
    vpc_verbose = Command(f'''aws ec2 describe-vpcs --profile {aws_creds} \
        --filters "Name=tag:Name,Values={vpc_name}"
        ''').strip().decode().split()
    for i in vpc_verbose:
        if 'dopt' in i:
            vpc_dhcpid = i.strip(',').strip('"')

    vpc_dhcp = Command(f'''aws ec2 describe-dhcp-options --profile {aws_creds} \
        --dhcp-options-ids {vpc_dhcpid}
        ''').strip().decode().split()
    for idx, val in enumerate(vpc_dhcp):
        if 'domain-name' in val and 'servers' not in val:
            dn = vpc_dhcp[idx + 5].strip('"')
        if 'domain-name-servers' in val:
            dc_idx_start = vpc_dhcp[idx:]
            for v in dc_idx_start:
                if 'Key' in v:
                    dc_idx_end = dc_idx_start.index(v)
            dc_idxs = vpc_dhcp[idx:idx + dc_idx_end]
            dcs = []
            for i, v in enumerate(dc_idxs):
                if '"Value"' in v:
                    dcs.append(dc_idxs[i + 1])
            for ip in dcs:
                dc_ips.append(ip.strip('"'))
        if 'ntp' in val:
            ntp_idx_start = vpc_dhcp[idx:]
            for v in ntp_idx_start:
                if 'Dhcp' in v:
                    ntp_idx_end = ntp_idx_start.index(v)
            ntp_idxs = vpc_dhcp[idx:idx + ntp_idx_end]
            ntp = []
            for i, v in enumerate(ntp_idxs):
                if '"Value"' in v:
                    ntp.append(ntp_idxs[i + 1])
            for ip in ntp:
                ntp_ips.append(ip.strip('"'))
                
    if 'domain' in info.lower():
        return dn
    if 'dcs' in info.lower():
        return dc_ips
    if 'ntp' in info.lower():
        return ntp_ips
    else:
        return dn, dc_ips, ntp_ips