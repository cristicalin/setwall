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

import os
import random
import pyinotify
import copy

from simplejson import *

import bst

# File list maintains a randomized list of files in a directory
# and behaves like a circular list so get_next and get_previous
# will never return an error.
# By design, this assumes there is at least one file in the
# directory it is monitoriing.
class filelist:

  # This is a handler used by PyINotify to watch contents of
  # wallpapers directory path and notify file_list of changes
  class handlereload(pyinotify.ProcessEvent):

    def __init__(self, list):
      self.LIST = list
      
    def process_IN_CLOSE_WRITE(self, event):
      if not event.dir:
        self.LIST.add_file(event.name)

    def process_IN_DELETE(self, event):
      if not event.dir:
        self.LIST.remove_file(event.name)

  def __init__(self, app = None):
    # Initialize the notifier and watch the folder for any changes
    # we only register to the create and delete events
    # we don't care about other events since they do not impact
    # the list of files in the directory
    self.WATCH_MANAGER = pyinotify.WatchManager()
    self.NOTIFIER = pyinotify.ThreadedNotifier(
      self.WATCH_MANAGER,
      self.handlereload(self)
    )
    self.NOTIFIER.start()
    self.DIR_PATH = None
    self.APP = app

  # Load the file list, either from the directory path or from a saved list
  # reconcile the saved list whith current file list
  def load(self, path, json = None):
    self.suspend_watch()
    # only reload if path changed
    if path != self.DIR_PATH:
      self.LOCAL_COUNT = 0
      self.DIR_PATH = path
      temp = os.walk(self.DIR_PATH).next()[2]
      temp_tree = bst.bst(temp)
      # if we have a saved state load that, else load clean list and randomize
      if json is not None:
        jd = JSONDecoder()
        self.LOCAL_FILE_LIST = jd.decode(json)
        # reconcile the JSON with the files actually in the folder
        for my_file in self.LOCAL_FILE_LIST:
          if temp_tree.extract(my_file) != my_file: 
            self.LOCAL_FILE_LIST.remove(my_file)
        self.LOCAL_FILE_LIST += temp_tree.as_list()
      else:
        self.LOCAL_FILE_LIST = temp
        self.randomize()
    self.instate_watch()
  
  # suspend the watch, we usually do this to avoid a race condition
  def suspend_watch(self):
    if self.DIR_PATH is not None:
      self.WATCH_MANAGER.del_watch(
        self.WATCH_MANAGER.get_wd(self.DIR_PATH)
      )
  
  # we instate the watch after the reace condition has passed
  # or upon a fresh load() call
  def instate_watch(self):
    self.WATCH_MANAGER.add_watch(
      self.DIR_PATH,
      pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE,
      rec=False
    )

  # we need to support copy in order to allow settings
  # to display preview of an independent file list
  # as Python usually passes references we need to use deepcopy()
  def __copy__(self):
    cp = filelist(self.APP)
    cp.DIR_PATH = copy.deepcopy(self.DIR_PATH)
    cp.LOCAL_COUNT= copy.deepcopy(self.LOCAL_COUNT)
    cp.LOCAL_FILE_LIST = copy.deepcopy(self.LOCAL_FILE_LIST)
    cp.instate_watch()
    return cp

  def get_json(self):
    je = JSONEncoder()
    return je.encode(self.LOCAL_FILE_LIST)

  def close(self):
    # This is to make sure we stop the inotify upon cleanup
    # unfortuantely Python does not guarantee the call to __del__
    # so I had to create this miserable hack
    self.NOTIFIER.stop()

  def get_next_file(self):
    self.LOCAL_COUNT += 1
    self.LOCAL_COUNT %= len(self.LOCAL_FILE_LIST)
    return self.get_current_file()

  def get_previous_file(self):
    self.LOCAL_COUNT -= 1
    self.LOCAL_COUNT %= len(self.LOCAL_FILE_LIST)
    return self.get_current_file()

  def get_current_file(self):
    tmp = "%s/%s" % (self.DIR_PATH, self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
    return tmp

  def set_index(self, file):
    try:
      self.LOCAL_COUNT = self.LOCAL_FILE_LIST.index(file)
    except ValueError:
      self.LOCAL_COUNT = 0

  def add_file(self, file):
    self.LOCAL_FILE_LIST.insert(self.LOCAL_COUNT+1, file)
    if self.APP is not None:
      self.APP.file_changed("add", "%s/%s" % (self.DIR_PATH, file))

  def remove_file(self, file):
    self.LOCAL_FILE_LIST.remove(file)
    if self.APP is not None:
      self.APP.file_changed("remove", "%s/%s" % (self.DIR_PATH, file))

  def get_list(self):
    return self.LOCAL_FILE_LIST

  def randomize(self):
    random.shuffle(self.LOCAL_FILE_LIST)

  def sort(self):
    self.LOCAL_FILE_LIST.sort()

  def reverse(self):
    self.LOCAL_FILE_LIST.reverse()


# For unit testing purposes only
if __name__ == "__main__":

  class callback:
    def file_changed(action, file):
      print "file_changed(%s: %s)" % (action, file)

  fl = filelist(callback())
  fl.load(".")
  l = fl.get_list()
  fl.close()

  print l
  print fl.get_current_file()
