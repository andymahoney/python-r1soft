#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Nexcess.net python-r1soft
# Copyright (C) 2013  Nexcess.net L.L.C.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging
import datetime
import collections

import r1soft

logger = logging.getLogger('cdp-backup-states')
logger.addHandler(logging.StreamHandler())

def read_config(config_filename):
    with open(config_filename) as f:
        config_raw = f.read().strip()
    keys = ['version', 'hostname', 'port', 'ssl', 'username', 'password']
    config = [dict(zip(keys, (field.strip() for field in line.strip().split(':')))) \
            for line in config_raw.split('\n') \
        if line.strip() and not line.startswith('#')]
    for key in ['version', 'port', 'ssl']:
        for server in config:
            server[key] = int(server[key])
    return config

def handle_cdp5_server(server):
    last_successful = None
    host_results = []
    status_counts= {}
    status_counts["OK"] = status_counts["ERROR"] = status_counts["ALERT"]=status_counts["UNKNOWN"]=status_counts["DISABLED"]=0
    
    client = r1soft.cdp3.CDP3Client(server['hostname'], server['username'],
        server['password'], server['port'], server['ssl'])

    for policy in client.Policy2.service.getPolicies():
        if not policy.enabled:
            status_counts["DISABLED"]+=1
            continue
        try:
            if last_successful is None:
                last_successful = policy.lastReplicationRunTime.replace(microsecond=0)
            elif last_successful < policy.lastReplicationRunTime:
                last_successful = policy.lastReplicationRunTime.replace(microsecond=0)
        except AttributeError:
            continue
        
        status_counts[policy.state]=status_counts[policy.state]+1
    return (last_successful, status_counts)

def handle_server(server):
    handle_func = {
        5:  handle_cdp5_server,
    }.get(server['version'])
    return handle_func(server)

if __name__ == '__main__':
    import sys

    try:
        config = read_config(sys.argv[1])
    except IndexError:
        logger.error('Config file must be the first CLI argument')
        sys.exit(1)

    for server in config:
        try:
            last_successful, status_counts = handle_server(server)
        except Exception as err:
            print '^ %s (CDP%d) ^ ERROR! ^' % (server['hostname'], server['version'])
            print '| %s | %s |' % (err.__class__.__name__, err)
        else:
            print server['hostname']
            print last_successful
            keys=sorted(status_counts.keys())
            for key in keys:
                print key  , status_counts[key]
            
