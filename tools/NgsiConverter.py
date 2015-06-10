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


import re
import os
import csv
import sys
import json
import getpass
import inspect
import requests

import ConfigParser
import functions as f


def get_new_token():
    user = raw_input("Username (e-mail): ")
    pswd = getpass.getpass(stream=sys.stderr, prompt="Password: ")

    data = {
        "username": user,
        "password": pswd,
    }

    payload = json.dumps(data)
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post("https://orion.lab.fiware.org/token", headers=headers, data=payload)

    if response.status_code == 200:
        file_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
        if not os.path.exists('%s/auth/auth.dat' % file_path):
            if not os.path.exists('%s/auth' % file_path):
                os.mkdir('%s/auth' % file_path)
            with open('%s/auth/auth.dat' % file_path, 'w') as json_file:
                j_data = json.dumps({'token': response.text})
                json_file.write(j_data)
                json_file.close()
    else:
        print response.json()['message']


def check_token(cb_url):

    file_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

    if not os.path.exists('%s/auth/auth.dat' % file_path):
        if not os.path.exists('%s/auth' % file_path):
            os.mkdir('%s/auth' % file_path)
        with open('%s/auth/auth.dat' % file_path, 'w') as json_file:
            j_data = json.dumps({'token': ''})
            json_file.write(j_data)
            json_file.close()

    with open('%s/auth/auth.dat' % file_path, 'r') as json_file:

        try:
            token = json.loads(json_file.read())['token']
            headers = {'Content-Type': 'application/json', "X-Auth-Token": token, 'Accept': 'application/json'}
            response = requests.post(cb_url, headers=headers)
            json_file.close()
            return response.status_code

        except ValueError:
            return 401



class NgsiConverter():

    def __init__(self):

        self.delimiter = ''
        self.quotechar = ''
        self.pos_delimiter = ''
        self.pos_pattern = ''
        self.pos_pattern2 = ''
        self.id_ = 'entity_id'
        self.pos_ = 'position_'
        self.cb = ''
        self.dm = ''

    def cb_config(self, conf_path):

        config = ConfigParser.RawConfigParser()
        config.read(conf_path)

        if 'cb_config' in config.sections():
            if 'cb_url' in config.options('cb_config') and config.get('cb_config', 'cb_url') != '':
                cb_url = config.get('cb_config', 'cb_url')
            else:
                raise ValueError("cb_url is a mandatory field at config_file")

            if 'tenant' in config.options('cb_config'):
                tenant = config.get('cb_config', 'tenant')
            else:
                tenant = ''

            if 'service_path' in config.options('cb_config'):
                service_path = config.get('cb_config', 'service_path')
            else:
                service_path = ''

            if 'need_token' in config.options('cb_config')and config.getboolean('cb_config', 'need_token'):
                if check_token(cb_url) == 401:
                    get_new_token()
            else:
                service_path = ''

        else:
            raise ValueError("cb_config is a mandatory section at config_file")

        self.cb = f.ContextBroker(cb_url, service_path=service_path, tenant=tenant)
        self.dm = self.cb.entity

    def config_data_parser(self, conf_path):

        config = ConfigParser.RawConfigParser()
        config.read(conf_path)

        if 'parser_config' in config.sections():
            if 'delimiter' in config.options('parser_config') and config.get('parser_config', 'delimiter') != '':
                self.delimiter = config.get('parser_config', 'delimiter')
            else:
                self.delimiter = ','

            if 'quotechar' in config.options('parser_config') and config.get('parser_config', 'quotechar') != '':
                self.quotechar = config.get('parser_config', 'quotechar')
            else:
                self.quotechar = '|'

            if ('pos_delimiter' in config.options('parser_config')
                    and config.get('parser_config', 'pos_delimiter') != ''):
                self.pos_delimiter = config.get('parser_config', 'pos_delimiter')
            else:
                self.pos_delimiter = ','
        else:
            self.delimiter = ','
            self.quotechar = '|'
            self.pos_delimiter = ','

        self.pos_pattern = '[0-9A-Za-z]+\%s[0-9A-Za-z]+$' % self.pos_delimiter
        self.pos_pattern2 = '\-?[0-9]{1,3}\.[0-9]*\,\-?[0-9]{1,3}\.[0-9]*$'

    def load_csv(self, csv_path):
        data_list = []
        with open(csv_path, 'rb') as csv_file:
            spam_reader = csv.reader(csv_file, delimiter=self.delimiter, quotechar=self.quotechar)
            for row in spam_reader:
                data_list.append(row)

        return data_list

    def load_conf(self, conf_path, data):
        try:
            config = ConfigParser.RawConfigParser()
            config.read(conf_path)
            if 'csv_config' not in config.sections():
                raise ValueError("csv_config section not found in the config file")

            _id = config.get('csv_config', self.id_)
            if _id == "":
                for e in range(len(data)):
                    if e == 0:
                        data[e].insert(0, '_id_')
                    else:
                        data[e].insert(0, str(e))
                _id = '_id_'

            data_dict = {self.id_: _id,
                         'entity_type': config.get('csv_config', 'entity_type')}

            if self.pos_ in config.options('csv_config'):
                data_dict[self.pos_] = config.get('csv_config', self.pos_)

            for element in data[0]:
                if element == '_id_':
                    data_dict[self.id_] = '_id_'
                else:
                    e_n = config.get('csv_config', '%s.name' % element)
                    e_t = config.get('csv_config', '%s.type' % element)

                    data_dict[element] = [e_n, e_t]

            if 'id_prefix' in config.options('csv_config'):
                data_dict['id_prefix'] = config.get('csv_config', 'id_prefix')

            return data_dict

        except Exception as e:
            print e
            exit(-1)

    def forbidden_index(self, data_conf, data_head):

        f_index = [data_head.index(data_conf[self.id_])]

        if self.pos_ in data_conf:
            if re.match(self.pos_pattern, data_conf[self.pos_].replace(" ", "")):
                pos = data_conf[self.pos_].replace(" ", "").split(self.pos_delimiter)
                f_index.append(data_head.index(pos[0]))
                f_index.append(data_head.index(pos[1]))

            elif data_conf[self.pos_].lower() in data_head:
                f_index.append(data_head.index(data_conf[self.pos_].lower()))

            else:
                raise ValueError("Bad definition of %s in the config file" % self.pos_)

        return f_index

    def parse_location(self, data_conf, data_head, entity_data, pos_index):
        pos_format = data_conf[data_head[pos_index[1]]][1]
        for a in pos_index[1:]:
            if pos_format != data_conf[data_head[a]][1]:
                raise ValueError("%s formats don't match" % str([data_conf[data_head[x]][0] for x in pos_index[1:]]))

        if pos_format == 'wgs84'or pos_format == 'EPSG:4326':
            coord = [entity_data[a] for a in pos_index[1:]]
            coord = str(coord).replace('[', '').replace(']', '').replace(' ', '').replace("'", "")
            coord = coord.replace(self.pos_delimiter, ',')

            pos_p = re.match(self.pos_pattern2, coord)
            if pos_p:
                self.dm.attribute.attribute_add('position', 'coords', value=pos_p.group())
                self.dm.attribute.metadata.metadata_add('location', 'string', 'WGS84')
                self.dm.attribute.add_metadatas_to_attrib('position')
                self.dm.attribute.metadata.metadata_list_purge()

    def parse_data(self, data_conf, data, del_=False):
        data_head = data[0]

        f_index = self.forbidden_index(data_conf, data_head)

        for entity in data[1:]:

            if entity[f_index[0]] != '':
                if 'id_prefix' in data_conf:
                    id_ = data_conf['id_prefix']+entity[f_index[0]]
                else:
                    id_ = entity[f_index[0]]

                self.dm.entity_add(id_, data_conf['entity_type'])

                for i in range(len(entity)):
                    if i not in f_index and entity[i] != '':
                        v = entity[i].replace("'", "").replace("(", "").replace(")", "").decode("utf-8")
                        self.dm.attribute.attribute_add(data_conf[data_head[i]][0], data_conf[data_head[i]][1], value=v)

                if len(f_index) > 1:
                    self.parse_location(data_conf, data_head, entity, f_index)

                if not del_:
                    self.dm.add_attributes_to_entity(id_)

            self.dm.attribute.attribute_list_purge()

    def transform(self, data_path, conf_path='', action='APPEND'):
        try:
            if conf_path == '':
                conf_path = data_path[:data_path.find('.')]+".ini"
            if not os.path.exists(data_path):
                details = "Cannot find the data file %s, please check if the path is correct" % data_path
                raise ValueError(details)
            if not os.path.exists(conf_path):
                conf_path = data_path[:data_path.find('.')]+".cfg"
                if not os.path.exists(conf_path):
                    details = """Cannot find a config file (*.cfg or *.ini) for %s,
                    please create it or define the config file path""" % data_path
                    raise ValueError(details)

            del_ = False
            if action == 'DELETE':
                del_ = True

            self.cb_config(conf_path)
            self.config_data_parser(conf_path)

            data = self.load_csv(data_path)
            conf = self.load_conf(conf_path, data)

            self.parse_data(conf, data, del_)
            print self.cb.update_context(action=action).text

        except IOError as e:
            print e
        except ValueError as e:
            print e
