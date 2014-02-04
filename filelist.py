#!/usr/bin/python

import os
import random
import pyinotify

from simplejson import *

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

  def __init__(self, callback = None):
    # Initialize the notifier and watch the folder for any changes
    # we only register to the create and delete events
    # we don't care about other events since they do not impact
    # the list of files in the directory
    self.WATCH_MANAGER = pyinotify.WatchManager()
    self.NOTIFIER = pyinotify.ThreadedNotifier(self.WATCH_MANAGER,
                                               self.handlereload(self))
    self.NOTIFIER.start()
    self.DIR_PATH = None
    self.CALLBACK = callback

  def load(self, path, json = None):
    if path != self.DIR_PATH:
      self.LOCAL_COUNT = 0
      if self.DIR_PATH is not None:
        self.WATCH_MANAGER.del_watch(self.DIR_PATH,
                                     pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE,
                                     rec=False)
      self.DIR_PATH = path
      temp = os.listdir(self.DIR_PATH)
      if json is not None:
        jd = JSONDecoder()
	self.LOCAL_FILE_LIST = jd.decode(json)
	# reconcile the JSON with the files actually in the folder
	for my_file in self.LOCAL_FILE_LIST:
	  if my_file in temp:
	    temp.remove(my_file)
	  else:
	    self.LOCAL_FILE_LIST.remove(my_file)
	    print my_file
	self.LOCAL_FILE_LIST += temp
      else:
        self.LOCAL_FILE_LIST = temp
	self.randomize()
      self.WATCH_MANAGER.add_watch(self.DIR_PATH,
                                   pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE,
                                   rec=False)

  def close(self):
    # This is to make sure we stop the inotify upon cleanup
    # unfortuantely Python does not guarantee the call to __del__
    # so I had to create this miserable hack
    self.NOTIFIER.stop()
    je = JSONEncoder()
    return je.encode(self.LOCAL_FILE_LIST)

  def get_next_file(self):
    self.LOCAL_COUNT += 1
    self.LOCAL_COUNT %= len(self.LOCAL_FILE_LIST)
    tmp = "%s/%s" % (self.DIR_PATH, self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
    return tmp

  def get_previous_file(self):
    self.LOCAL_COUNT -= 1
    self.LOCAL_COUNT %= len(self.LOCAL_FILE_LIST)
    tmp = "%s/%s" % (self.DIR_PATH, self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
    return tmp

  def set_index(self, file):
    try:
      self.LOCAL_COUNT = self.LOCAL_FILE_LIST.index(file)
    except ValueError:
      self.LOCAL_COUNT = 0

  def add_file(self, file):
    self.LOCAL_FILE_LIST.insert(self.LOCAL_COUNT+1, file)
    if self.CALLBACK is not None:
      self.CALLBACK("add", "%s/%s" % (self.DIR_PATH, file))

  def remove_file(self, file):
    self.LOCAL_FILE_LIST.remove(file)
    if self.CALLBACK is not None:
      self.CALLBACK("remove", "%s/%s" % (self.DIR_PATH, file))

  def get_list(self):
    return self.LOCAL_FILE_LIST

  def randomize(self):
    random.shuffle(self.LOCAL_FILE_LIST)

  def sort(self):
    self.LOCAL_FILE_LIST.sort()


# For unit testing purposes only
if __name__ == "__main__":

  def callback(action, file):
    print "%s: %s" % (action, file)

  fl = filelist(callback)
  fl.load(".")
  l = fl.get_list()
  o = fl.close()
  j = JSONDecoder()
  print j.decode(o)
