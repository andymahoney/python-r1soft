
Sort the ouput of list-agents so that it sorts by agent version
list-agents.py  -uAPIUSER -pPASSWORD HOSTNAME|sort -k 2 -V -t ','

Takes a config file of the format that cdp-get-failed-backups takes
Only implemented for CDP5
cdp-backup-states CONFIGFILE

config file format
CPDVERSION:HOSTNAME:PORT:SSL(0|1):USER:PASSWORD

