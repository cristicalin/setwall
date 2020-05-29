#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import os.path
import random
import copy
import threading
import logging

import pyinotify

from .bst import bst

from .utils import *

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
      pyinotify.ProcessEvent.__init__(self)

    def add(self, event):
      if not event.dir:
        self.LIST.add_file(event.name)

    def remove(self, event):     
      if not event.dir:
        self.LIST.remove_file(event.name)
      
    def process_IN_CLOSE_WRITE(self, event):
      self.add(event)

    def process_IN_MOVED_TO(self, event):
      self.add(event)

    def process_IN_DELETE(self, event):
      self.remove(event)

    def process_IN_MOVED_FROM(self, event):
      self.remove(event)

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
    self.SETTINGS = app.SETTINGS
    self.NEED_SAVE = False
    self.LOCAL_FILE_LIST_LOCK = threading.Lock()
    self.NEED_RECONCILE = True
    self.RESTRICTED = False

  # Load the file list, this saves time walking large folders
  def load_from_list(self, path, the_list):
    if the_list is not None and len(the_list) > 0:
      self.suspend_watch()
      self.DIR_PATH = path
      self.set_list(the_list)
      self.instate_watch()
      self.NEED_RECONCILE = True
    else:
      self.load_from_path(path)

  # Load file directly from disk, this is sub-optimal in case of large folders
  def load_from_path(self, path):
    self.suspend_watch()
    self.DIR_PATH = path
    tmp = get_file_list(self.DIR_PATH, self.SETTINGS.get_wallpaper_recursive())
    self.set_list(tmp)
    self.instate_watch()
    self.NEED_RECONCILE = False

  # reconcile in memory list with actual state on disk
  # used from the cli to reconcile file system state if differing from json
  def _reconcile(self):
    if self.NEED_RECONCILE:
      self.suspend_watch()
      temp = get_file_list(self.DIR_PATH, self.SETTINGS.get_wallpaper_recursive())
      temp_tree = bst(temp)
      for my_file in self.LOCAL_FILE_LIST:
        if temp_tree.extract(my_file) != my_file: 
          self.list_remove(my_file)
      temp_list = temp_tree.as_list()
      if len(temp_list) > 0:
        self.LOCAL_FILE_LIST += temp_tree.as_list()
      self.NEED_SAVE = True
      self.instate_watch()
    self.NEED_RECONCILE = False

  # we need to execute this in a separate thread because on large folders
  # this takes a while to return and dbus invocation will throw an error
  def reconcile(self):
    thread = threading.Thread(target=self._reconcile)
    thread.start()

  # suspend the watch, we usually do this to avoid a race condition
  def suspend_watch(self):
    if self.DIR_PATH is not None:
      watch = self.WATCH_MANAGER.get_wd(self.DIR_PATH)
      if watch is not None:
        self.WATCH_MANAGER.del_watch(watch)
  
  # we instate the watch after the reace condition has passed
  # or upon a fresh load_from_*() or reconcile() call
  def instate_watch(self):
    # only instate a new watch if another one is not already present
    if self.DIR_PATH is not None:
      watch = self.WATCH_MANAGER.get_wd(self.DIR_PATH)
      if watch is None:
        self.WATCH_MANAGER.add_watch(
          self.DIR_PATH,
          pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE |
          pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO,
          rec=False
        )

  # we need to support copy in order to allow settings
  # to display preview of an independent file list
  # as Python usually passes references we need to use deepcopy()
  def __copy__(self):
    cp = filelist(self.APP)
    cp.DIR_PATH = copy.deepcopy(self.DIR_PATH)
    cp.LOCAL_COUNT= copy.deepcopy(self.LOCAL_COUNT)
    cp.set_list(copy.deepcopy(self.LOCAL_FILE_LIST))
    cp.instate_watch()
    cp.NEED_SAVE = True
    return cp

  def get_json(self):
    return to_json(self.LOCAL_FILE_LIST)

  def close(self):
    # This is to make sure we stop the inotify upon cleanup
    # unfortuantely Python does not guarantee the call to __del__
    # so I had to create this miserable hack
    try:
      self.suspend_watch()
      self.NOTIFIER.stop()
    except:
      None

  def _get_file(self, add):
    if len(self.LOCAL_FILE_LIST) <= 0:
      return None
    self.LOCAL_COUNT += add
    self.LOCAL_COUNT %= len(self.LOCAL_FILE_LIST)
    try:
      full_filename = "%s/%s" % (self.DIR_PATH,
                                 self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
      filename = self.LOCAL_FILE_LIST[self.LOCAL_COUNT]
      if self.SETTINGS.get_verify_presence():
        if not os.path.isfile(full_filename):
          self.LOCAL_FILE_LIST.remove(filename)
          return None
      if self.SETTINGS.get_verify_image():
        if not is_image(full_filename):
          self.LOCAL_FILE_LIST.remove(filename)
          return None
      return full_filename
    except Exception as e:
      logging.error(e)
      return None

  def _get_file_counter(self, add, counter = 5):
    current_file = self._get_file(add)
    logging.warning(current_file)
    if current_file is None:
      if counter > 0:
        return self._get_file_counter(add, counter - 1)
      else:
        return None
    else:
      return current_file

  def get_next_file(self):
    return self._get_file_counter(1)

  def get_previous_file(self):
    return self._get_file_counter(-1)

  def get_current_file(self):
    return self._get_file_counter(0)

  def get_path(self):
    return self.DIR_PATH

  def set_path(self, path, restricted = False):
    self.suspend_watch()
    self.DIR_PATH = path
    self.RESTRICTED = restricted
    if not restricted:
      self.instate_watch()

  def get_restricted(self):
    return self.RESTRICTED

  def set_index(self, file):
    try:
      self.LOCAL_COUNT = self.list_index(file)
    except:
      self.LOCAL_COUNT = 0

  def add_file(self, file):
    self.list_insert(self.LOCAL_COUNT+1, file)
    if self.APP is not None:
      self.APP.file_changed("add", "%s/%s" % (self.DIR_PATH, file))

  def remove_file(self, file):
    self.list_remove(file)
    if self.APP is not None:
      self.APP.file_changed("remove", "%s/%s" % (self.DIR_PATH, file))

  def get_list(self):
    return self.LOCAL_FILE_LIST

  def do_locked_op(self, obj, func):
    self.LOCAL_FILE_LIST_LOCK.acquire()
    try:
      ret = func(self.LOCAL_FILE_LIST, obj)
      self.set_need_save(True)
    finally:
      self.LOCAL_FILE_LIST_LOCK.release()
    return ret

  def set_list(self, new_list):
    self.LOCAL_FILE_LIST_LOCK.acquire()
    try:
      self.LOCAL_FILE_LIST = new_list
      self.set_need_save(True)
    finally:
      self.LOCAL_FILE_LIST_LOCK.release()

  def list_append(self, new_list):
    self.LOCAL_FILE_LIST_LOCK.acquire()
    try:
      self.LOCAL_FILE_LIST += new_list
      self.set_need_save(True)
    finally:
      self.LOCAL_FILE_LIST_LOCK.release()

  def list_insert(self, pos, obj):
    self.do_locked_op(obj, lambda a, b: a.insert(pos, b))

  def list_remove(self, obj):
    self.do_locked_op(obj, lambda a, b: a.remove(b))

  def list_index(self, obj):
    return self.do_locked_op(obj, lambda a, b: a.index(b))

  def randomize(self):
    self.do_locked_op(None, lambda a, b: random.shuffle(a))

  def sort(self):
    self.do_locked_op(None, lambda a, b: a.sort())

  def reverse(self):
    self.do_locked_op(None, lambda a, b: a.reverse())

  def get_need_save(self):
    return self.NEED_SAVE

  def set_need_save(self, value):
    self.NEED_SAVE = value

  # allow forcing a reconcile, this needs to be called first
  def invalidate(self):
    self.NEED_RECONCILE = True

# For unit testing purposes only
if __name__ == "__main__":

  class callback:
    def file_changed(action, file):
      print("file_changed(%s: %s)" % (action, file))

  fl = filelist(callback())
  fl.load_from_path(".")
  l = fl.get_list()
  fl.close()

  print(l)
  print(fl.get_current_file())
