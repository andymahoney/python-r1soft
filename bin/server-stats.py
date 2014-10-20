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

if __name__ == '__main__':
    import r1soft
    import subprocess
    import re
    parser = r1soft.util.build_option_parser()
    parser.remove_option('--r1soft-host')
    parser.add_option('-d', '--decoration',
        help='Add decoration to the CDP hostname when printing the agents for ' \
            'multiple servers. Leave blank (default) to supress printing the CDP hostname')
    opts, args = parser.parse_args()

    for host in args:
        client = r1soft.cdp3.CDP3Client(host, opts.username, opts.password)
        if opts.decoration:
            print opts.decoration + host + opts.decoration[::-1]
	info = client.Configuration.service.getServerInformation()
	more = client.Configuration.service.getServerLicenseInformation()
	tasks = client.Configuration.service.getTaskSchedulerStatistics()
	print "Configured heap " + str(info.maxConfiguredHeapMemory)
	print "Heap commited " + str(info.heapMemoryInformation.committed)
	print "Heap initial " + str(info.heapMemoryInformation.initial)
	print "Heap maximum " + str(info.heapMemoryInformation.maximum)
	print "Heap used " + str(info.heapMemoryInformation.used)
	print "nonHeap commited " + str(info.nonHeapMemoryInformation.committed)
	print "nonHeap initial " + str(info.nonHeapMemoryInformation.initial)
	print "nonHeap maximum " + str(info.nonHeapMemoryInformation.maximum)
	print "nonHeap used " + str(info.nonHeapMemoryInformation.used)
	print "Free Physical " + str(info.freePhysicalMemory)
	try:
		more.version = re.match('^\d+\.\d+\.\d+', more.version).group()
		
	except AttributeError:
		more.version = str(subprocess.check_output("rpm -qa '*serverbackup-manager*' --qf '%{VERSION}'",shell=True))
	print  "Server Version " + str(more.version)
	for pool in client.Configuration.service.getTaskSchedulerStatistics():
		print pool[0] + " queue size " + str(pool[1].queueSize)
		print pool[0] + " thread count " + str(pool[1].runningThreadCount)
	bad_agents=total_agents=unknown_agents=outdated_agents=upgraded_agents=0
	for agent in client.Agent.service.getAgents():
            try:
                agent.lastKnownAgentVersion
            except AttributeError:
#                print agent.description + ", Unknown"
		unknown_agents+=1
		bad_agents+=1
		total_agents+=1
            else:
                agent.lastKnownAgentVersion = re.match('^\d+\.\d+\.\d+', agent.lastKnownAgentVersion).group(0)
		total_agents+=1
                if  agent.lastKnownAgentVersion < more.version:
			outdated_agents+=1
			bad_agents+=1
		elif agent.lastKnownAgentVersion > more.version:
			upgraded_agents+=1
			bad_agents+=1
	print "Total Agents " + str(total_agents)
	print "Outdated Agents " + str(outdated_agents)
	print "Upgraded Agents " + str(upgraded_agents)
	print "Unknown Agents " + str(unknown_agents)
	print "Bad Agents " + str(bad_agents)

#        for agent in client.Agent.service.getAgents():
#            try:
#                agent.lastKnownAgentVersion
#            except AttributeError:
#                print agent.description + ", Unknown"
#            else:#                print agent.description + ", " + agent.lastKnownAgentVersion
