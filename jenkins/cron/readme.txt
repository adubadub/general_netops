Assumptions:
1. Jenkins running on Linux
2. Jenkins server running rsyslog
3. Jenkins forwarding to Splunk or syslog server

Steps:
# On Jenkins
1. Create /etc/rsyslog.d/jenkins.conf
2. Edit /etc/rsyslog.conf
3. Create /var/log/jenkins_build.log
4. Create /var/log/jenkins/jenkins_custom.log
5. Restart rsyslog (service rsyslog restart)
6. Create /usr/local/bin/check_workspace.py
7. Create /usr/local/bin/check_workspace.json
8. Create /usr/local/bin/job_list.txt
9. Modify crontab -e

Outcome:
The above changes will forward job execution RESULTS to Splunk in below format:
<mon> <d> <hh:mm:ss> <jenkins server name> Jenkins Run#execute: <job name> <build no> main build action completed: <SUCCESS/FAILURE>

Use-case:
You'd like to alert/log on job execution status, but are trying to avoid logging full job execution console output (which may include sensitive information in clear text). 