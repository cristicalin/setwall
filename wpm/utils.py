#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SetWall - Wallpaper manager
# 
# Copyright (C) 2014,2015  Cristian Andrei Calin <cristian.calin@outlook.com>
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
import hashlib
import msgpack
import zlib
import base64

from gi.repository import Gio as gio

from functools import partial
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
    if check_func("%s/%s" % (directory, i)) and not i.startswith("."):
      file_list.append(i)
  return file_list

# Walk the file list to build up
def _walk_files(file_list, directory, dir_path, files):
  for f in files:
    # include only non-hidden files
    if not f.startswith("."):
      path = dir_path.replace(directory, "")
      tmp = ("%s/%s" % (path, f)).lstrip("/")
      if len(tmp) > 0:
        file_list.append(tmp)

# Walk the file list to build up
def _walk_dirs(dir_list, directory, dir_path, files):
  tmp = (dir_path.replace(directory, "")).lstrip("/")
  if len(tmp) > 0:
    dir_list.append(tmp.lstrip("/"))

# Get the recursive file list
def get_recursive_list(directory, func):
  my_list = []
  for dir_path, subdirs, files_list in os.walk(directory):
    for sdir in subdirs:
      if sdir.startswith("."):
        subdirs.remove(sdir)
    func(my_list, directory, dir_path, files_list)
  return my_list

# Get file list from a directory
def get_file_list(directory, recursive = False):
  if recursive:
    return get_recursive_list(directory.rstrip("/"), _walk_files)
  else:
    return get_checked_list(directory, lambda a: os.path.isfile(a))

# Get subdir list from a directory
def get_dir_list(directory, recursive = False):
  if recursive:
    return get_recursive_list(directory.rstrip("/"), _walk_dirs)
  else:
    return get_checked_list(directory, lambda a: os.path.isdir(a))

# Compute md5sum
def md5sum(filename):
  with open(filename, mode='rb') as f:
    d = hashlib.md5()
    for buf in iter(partial(f.read, 128), b''):
      d.update(buf)
  return d.hexdigest()

# Check if a specified file is a valid image by looking at the content type
def is_image(filename):
  file_handle = gio.File.new_for_path(filename)
  query_info = file_handle.query_info(
    "standard::content-type", gio.FileQueryInfoFlags.NONE, None
  )
  (base, specific) = query_info.get_content_type().split("/")
  return (base == "image")

# Encode/Decode a huge list to optimize disk space
def encode_list(my_list):
  msg = msgpack.dumps(my_list)
  zmsg = zlib.compress(msg)
  return str(base64.standard_b64encode(zmsg))

def decode_list(my_text):
  # we assume this is a valid encoded object
  # otherwise we return an empty list
  try:
    zmsg = base64.standard_b64decode(my_text)
    msg = zlib.decompress(zmsg)
    my_list = msgpack.loads(msg, encoding="utf-8")
    return my_list
  except:
    return []

# this is for unit testing only
if __name__ == "__main__":
  
  print(shorten("very long string more than 16 chars in length", 16))

  print(to_json({"abd":["dwds", "dda"]}))

  print(get_file_list("/dev/", True))

  print(get_dir_list("/dev/", True))

  my_list = ["apples", "oranges", "plums", "grapes"]
  print(my_list)
  my_txt = encode_list(my_list)
  decoded_list = decode_list(my_txt)
  print(decoded_list)
  if cmp(my_list, decoded_list) != 0:
    print("Encode/Decode failed")
  else:
    print("Encode/Decode success")
