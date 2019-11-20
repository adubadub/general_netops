This project assumes a few things:
1. A separate job gets backups of these devices and stores them on a fileserver
2. Backup file names include the device type (F5, Router, Fortigate, etc.)
3. Backup file types are .txt
4. This job will be run from an automation tool (Jenkins, etc.) with access to scm where py files will be stored