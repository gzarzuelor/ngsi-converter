#!/usr/bin/python
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of NgsiConverter.
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
# along with NgsiConverter. If not, see http://www.gnu.org/licenses/.

__author__ = 'gzarrub'

import os
import json
import inspect
import requests
import DataManager as DM



class ContextBroker():
    def __init__(self, cb_url, service_path='', tenant=''):
        """
        Add a new entity list if it is valid.
            :param cb_url: Context Broker URL
            :param user: user (Only for http://orion.lab.fiware.org:1026)
            :param password: password (Only for http://orion.lab.fiware.org:1026)
        """
        self.service_path = service_path
        self.tenant = tenant

        self.orion = False
        if cb_url.find("http://orion.lab.fiware.org:1026") != -1:
            self.orion = True
            self.token = ''
            self.get_auth_token()

        if cb_url[len(cb_url)-1] == '/':
            cb_url = cb_url[:len(cb_url)-1]

        self.CBurl = cb_url
        self.entity = DM.Entity()

    def get_auth_token(self):
        """
        Returns token IDM .
            :rtype : unicode
        """
        try:
            file_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

            if not os.path.exists('%s/auth/auth.dat' % file_path):
                if not os.path.exists('%s/auth' % file_path):
                    os.mkdir('%s/auth' % file_path)
                with open('%s/auth/auth.dat' % file_path, 'w') as json_file:
                    j_data = json.dumps({'token': ''})
                    json_file.write(j_data)
                    json_file.close()

            with open('%s/auth/auth.dat' % file_path, 'r') as json_file:
                self.token = json.loads(json_file.read())['token']
                json_file.close()

        except Exception as e:
            msg = "OrionAction.get_auth_token(): %s" % e
            DM.data_manager_error(msg)

    def clean_all(self):
        """
        Sets all the lists to empty lists.
        """
        self.entity.attribute.metadata.metadata_list_purge()
        self.entity.attribute.attribute_list_purge()
        self.entity.entity_list_purge()

    def get_response(self, data, url):
        """
        Context Broker request
            :param data:
            :param url:
            :rtype : requests.models.Response
        """
        try:
            if self.orion:
                headers = {'Content-Type': 'application/json', "X-Auth-Token": self.token, 'Accept': 'application/json'}
            else:
                headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

            if self.tenant != '':
                headers['Fiware-Service'] = self.tenant
            if self.service_path != '':
                headers['Fiware-ServicePath'] = self.service_path

            response = requests.post(url, headers=headers, data=data)
            return response

        except requests.RequestException as e:
            msg = "ContextBroker.get_response(): %s" % e.message
            DM.data_manager_error(msg)

    def update_context(self, action='APPEND'):
        """
        Context Broker updateContext function
            :param action: update context action ['APPEND', 'UPDATE', 'DELETE']
            :rtype : requests.models.Response
        """
        if action not in ['APPEND', 'UPDATE', 'DELETE']:
            msg = "ContextBroker.update_context():The action passed to the function was not valid"
            DM.data_manager_error(msg)

        if len(self.entity.get_entity_list()) == 0:
            msg = "ContextBroker.update_context(): Empty entity_list was passed to the function"
            DM.data_manager_error(msg)

        payload = {'contextElements': self.entity.get_entity_list(),
                   'updateAction': action}

        data = json.dumps(payload)
        url = self.CBurl+'/v1/updateContext'
        response = self.get_response(data, url)

        if response.status_code == 401:
            msg = "ContextBroker.query_context(): User token not authorized."
            DM.data_manager_error(msg)

        self.clean_all()

        return response




