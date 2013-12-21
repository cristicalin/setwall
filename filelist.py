#!/usr/bin/python

import os
import random

# File list maintains a randomized list of files in a directory
# and behaves like a circular list so get_next and get_previous
# will never return an error.
# By design, this assumes there is at least one file in the
# directory it is monitoriing.
class filelist:

  def __init__(self, path):
    self.LOCAL_COUNT = 0
    self.DIR_PATH = path
    self.LOCAL_FILE_LIST = os.listdir(self.DIR_PATH)
    random.shuffle(self.LOCAL_FILE_LIST)

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

  def remove_file(self, file):
    self.LOCAL_FILE_LIST.remove(file)

  def get_list(self):
    return self.LOCAL_FILE_LIST

if __name__ == "__main__":
  fl = filelist(".")
  print fl.get_list()

