# Copyright 2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Mandelbrot.
#
# Mandelbrot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mandelbrot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mandelbrot.  If not, see <http://www.gnu.org/licenses/>.

import collections, time
from tabulate import tabulate

def sort_results(results, sortfields, converters=None):
    """
    """
    def extractkey(row):
        key = list()
        for column in sortfields:
            if not column in row:
                key.append(None)
            else:
                value = row[column]
                if converters is not None and column in converters:
                    convert = converters[column]
                    key.append(convert(value))
                else:
                    key.append(value)
        return key
    return sorted(results, key=extractkey)

class OrderedMap(collections.Mapping):
    """
    """
    def __init__(self, mapping, keys):
        self._mapping = dict()
        self._keys = list()
        for key in keys:
            if key in mapping:
                self._mapping[key] = mapping[key]
                self._keys.append(key)
    def __getitem__(self, key):
        return self._mapping[key]
    def __iter__(self):
        return iter(self._keys)
    def __len__(self):
        return len(self._mapping)

def render_table(results, expand=True, columns=None, renderers=None, tablefmt='simple'):
    """
    """
    data = dict()
    numrows = 0

    # pre-populate data columns if specified
    if columns is not None:
        for name in columns:
            data[name] = list()

    # append each row to the table
    for row in results:
        for name,value in row.items():
            # if schema converter function is defined, then convert the value
            if renderers is not None and name in renderers:
                render = renderers[name]
                value = render(value)
            # if column exists, then append new value 
            try:
                column = data[name]
                column.append(value)
            except KeyError:
                # else if expand is true, create column and append new value
                if expand == True:
                    column = [None for _ in xrange(numrows)]
                    column.append(value)
                    data[name] = column
        # if row doesn't have a value for any existing columns, then fill with None
        for name in data.keys():
            if not name in row:
                column = data[name]
                column.append(None)
        # increment the row count
        numrows += 1

    # possibly change the order of columns
    headers = list()
    if columns is not None:
        for name in columns:
            headers.append(name)
    for name in sorted(set(tuple(data.keys())) - set(tuple(headers))):
        headers.append(name)
    table = OrderedMap(data, headers)

    # render the table
    return tabulate(table, headers, tablefmt)

def millis2ctime(millis):
    return time.ctime(millis / 1000.0)

def bool2checkbox(value):
    if value == True:
        return "*"
    return ""

def bool2string(value):
    if value == True:
        return "true"
    return "false"
