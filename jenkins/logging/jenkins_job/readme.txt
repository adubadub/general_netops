INITIAL BUILD--
1. Create /etc/rsyslog.d/jenkins.conf (see template)
2. Edit /etc/rsyslog.conf (see template)
3. Create /var/log/jenkins_build.log 
4. Create /var/log/jenkins/jenkins_custom.log
5. Restart rsyslog (service rsyslog restart)
8. Create /usr/local/bin/check_workspace.json (see template)
9. Create /usr/local/bin/job_list.txt

DETAILS--
check_workspace.py will parse both the jenkins default log 
as well as build specific console logs, consolidate the
desired information and create the new log on 
/var/log/jenkins/jenkins_custom.log.

From there, rsyslog will read from that custom log 
(via /etc/rsyslog.d/jenkins.conf), write what it matches to 
/var/log/jenkins_build.log and forward to a syslog server
(via /etc/rsyslog.conf).

Additionally, both /usr/local/bin/job_list.txt and 
/usr/local/bin/check_workspace.json will act as 
'state' files for reference as to which jobs/builds
need to be logged (i.e. which jobs/builds are new).
These are kept out of the jenkins workspace for 
posterity.

ASSUMPTIONS--
1. Jenkins running on Linux
2. Jenkins server running rsyslog
3. Jenkins forwarding to Splunk or syslog server