#!/usr/bin/python

# SetWall - Wallpaper manager
# 
# Copyright (C) 2014  Cristian Andrei Calin <cristian.calin@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# this code library contains useful stand alone functions

import os
import os.path

from simplejson import *

# Shorten long file names
def shorten(data, length):
  info = (data[:int(length/2)-1] + '..' + 
          data[-(int(length/2)-1):]) if len(data) > length else data
  return info

# Encode as JSON
def to_json(data):
  je = JSONEncoder(ensure_ascii = False)
  return je.encode(data)

# Decode from JSON
def from_json(json):
  jd = JSONDecoder()
  return jd.decode(json)

# Generic get function
def get_checked_list(directory, check_func):
  file_list = []
  tmp = os.listdir(directory)
  for i in tmp:
    if check_func("%s/%s" % (directory, i)):
      file_list.append(i)
  return file_list

# Get file list from a directory (os.listdir is much faster than os.walk for large folders)
def get_file_list(directory):
  return get_checked_list(directory, lambda a: os.path.isfile(a))

# Get subdir list from a directory (os.listdir is much faster than os.walk for large folders)
def get_dir_list(directory):
  return get_checked_list(directory, lambda a: os.path.isdir(a))

# this is for unit testing only
if __name__ == "__main__":
  
  print shorten("very long string more than 16 chars in length", 16)

  print to_json({"abd":["dwds", "dda"]})
