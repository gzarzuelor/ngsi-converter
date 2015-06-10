#!/usr/bin/python
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of context-broker-periodical-action.
#
# NgsiConverter is free software: you can redistribute
# it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# NgsiConverter is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.

__author__ = 'gzarrub'

import tools.NgsiConverter as NC
import sys

args = ['-f', '-cf', '-a']
args_index = []

for arg in sys.argv:
    if arg[0] == '-' and arg not in args:
        print "ngsi_converter.py -f [file] -cf [config_file] -a [action]"
        exit(-1)


if '-f' not in sys.argv:
    print "ngsi_converter.py -f [file] -cf [config_file] -a [action]"
    exit(-1)

if '-a' not in sys.argv:
    action = 'APPEND'

args_dict = {}
item = ''
for arg in sys.argv[1:]:
    if arg in args:
        item = arg
        args_dict[item] = []
    else:
        args_dict[item].append(arg)

n = NC.NgsiConverter()
if '-cf' in args_dict:
    if len(args_dict['-f']) == len(args_dict['-cf']):
        for i in range(len(args_dict['-f'])):
            n.transform(args_dict['-f'][i], conf_path=args_dict['-cf'][i], action=action)

    elif len(args_dict['-cf']) == 1:
        for i in range(len(args_dict['-f'])):
            n.transform(args_dict['-f'][i], conf_path=args_dict['-cf'][0], action=action)
    else:
        print "Config files don't match with data files"
        exit(-1)

else:
    for i in range(len(args_dict['-f'])):
        n.transform(args_dict['-f'][i], action=action)




