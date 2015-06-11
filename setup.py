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


from setuptools import setup, find_packages

setup(
    name='NgsiConverter',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/gzarrub/ngsi-converter',
    license='',
    author='Guillermo Zarzuelo',
    author_email='gzarrub@gmail.com',
    description="""The NgsiConverter is a python software that allows to transform
    csv files into an entry at a ContextBroker""",
    install_requires=['requests']
)