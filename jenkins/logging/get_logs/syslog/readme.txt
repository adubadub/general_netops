Assumptions:
1. Jenkins running on Linux
2. Jenkins server running rsyslog
3. Jenkins forwarding to Splunk (UniversalForwarder) on Linux

Steps:
# On Jenkins
1. Create /etc/rsyslog.d/jenkins.conf
2. Edit /etc/rsyslog.conf
3. Restart rsyslog (service rsyslog restart)
# On Splunk Forwarder
1. Edit /data/splunk/etc/system/local/props.conf
2. Edit /data/splunk/etc/system/local/inputs.conf
3. Restart Splunk (/data/splunk/bin/splunk restart)

Outcome:
The above changes will forward job execution RESULTS to Splunk in below format:
<mon> <d> <hh:mm:ss> <jenkins server name> Jenkins Run#execute: <job name> <build no> main build action completed: <SUCCESS/FAILURE>

Use-case:
You'd like to alert/log on job execution status, but are trying to avoid logging full job execution console output (which may include sensitive information in clear text). 