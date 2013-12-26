#!/usr/bin/python

import os
import random
import pyinotify

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

  def load(self, path):
    if path != self.DIR_PATH:
      self.LOCAL_COUNT = 0
      if self.DIR_PATH is not None:
        self.WATCH_MANAGER.del_watch(self.DIR_PATH,
                                     pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE,
                                     rec=False)
      self.DIR_PATH = path
      self.LOCAL_FILE_LIST = os.listdir(self.DIR_PATH)
      self.WATCH_MANAGER.add_watch(self.DIR_PATH,
                                   pyinotify.IN_DELETE | pyinotify.IN_CLOSE_WRITE,
                                   rec=False)
      self.randomize()

  def close(self):
    # This is to make sure we stop the inotify upon cleanup
    # unfortuantely Python does not guarantee the call to __del__
    # so I had to create this miserable hack
    self.NOTIFIER.stop()

  def get_next_file(self):
    self.LOCAL_COUNT += 1
    if self.LOCAL_COUNT >= len(self.LOCAL_FILE_LIST):
      self.LOCAL_COUNT = 0
    tmp = "%s/%s" % (self.DIR_PATH, self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
    return tmp

  def get_previous_file(self):
    self.LOCAL_COUNT -= 1
    if self.LOCAL_COUNT < 0:
      self.LOCAL_COUNT = len(self.LOCAL_FILE_LIST) - 1
    tmp = "%s/%s" % (self.DIR_PATH, self.LOCAL_FILE_LIST[self.LOCAL_COUNT])
    return tmp

  def set_index(self, file):
    while self.LOCAL_COUNT < len(self.LOCAL_FILE_LIST):
      if self.LOCAL_FILE_LIST[self.LOCAL_COUNT] == file:
        return
      self.LOCAL_COUNT += 1

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
  print fl.get_list()
  fl.close()