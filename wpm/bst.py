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

# This is an implementation of binary search tree
# optimized for searching content
class bst:
  
  def __init__(self, value=None):
    self.root = node(value)

  def __str__(self):
    return str(self.root)

  def as_list(self):
    if self.root is not None:
      return self.root.as_list()
    else:
      return []

  def insert(self, value):
    self.root.insert(value)

  def search(self, value):
    return self.root.search(value)

  def extract(self, value):
    if self.root is None:
      return None
    elif self.root.value == value:
      temp_root = node()
      temp_root.left = self.root
      result = self.root.extract(value, temp_root)
      self.root = temp_root.left
      return result
    else:
      return self.root.extract(value, self.root)

# The node implementation
class node:

  # class constructuctor, takes single value or a list
  def __init__(self, value=None, root=None):
    self.left = None
    self.right = None
    self.root = root
    if type(value) is list:
      self.value = None
      for i in value:
        self.insert(i)
    else:
      self.value = value

  # print as a string
  def __str__(self):
    return "[%s, %s, %s]" % (self.left, str(self.value), self.right)

  # convert to an ordered list
  def as_list(self):
    result = []
    if self.value is not None:
      result += [ self.value ]
    if self.left is not None:
      result = self.left.as_list() + result
    if self.right is not None:
      result += self.right.as_list()
    return result

  # check if this tree is empty
  def isEmpty(self):
    return self.left == self.right == self.value == None

  # insert an element in the right position in the tree
  def insert(self, value):
    if self.isEmpty():
      self.value = value
    elif value < self.value:
      if self.left is None:
        self.left = node(value, self)
      else:
        self.left.insert(value)
    else:
      if self.right is None:
        self.right = node(value, self)
      else:
        self.right.insert(value)

  # search for an element in the tree, complexity is log(n)
  def search(self, value):
    if self.isEmpty():
      return None
    elif value < self.value:
      if self.left is not None:
        return self.left.search(value)
    elif value > self.value:
      if self.right is not None:
        return self.right.search(value)
    else:
      return self.value

  # return minimum value
  def min_value(self):
    if (self.left is None):
       return self.value
    else:
       return self.left.min_value()

  # extract an element from the tree, first we need to find it
  # then find the right most element in the tree
  # and swap the right most element for the current value
  def extract(self, value, parent):
    if self.isEmpty():
      return None
    elif value < self.value:
      if self.left is not None:
        return self.left.extract(value, self)
    elif value > self.value:
      if self.right is not None:
        return self.right.extract(value, self)
    else:
      # found the element, need to find the right most one
      result = self.value
      if self.left is not None and self.right is not None:
	self.value = self.right.min_value()
	self.right.extract(self.value, self)
      elif parent.left == self:
        if self.left is not None:
	  parent.left = self.left
	else:
	  parent.left = self.right
      elif parent.right == self:
        if self.left is not None:
	  parent.right = self.left
	else:
	  parent.right = self.right
      else:
        parent.value = None
      return result


if __name__ == "__main__":
  import os
  import random
  import sys
  reload(sys)
  sys.setdefaultencoding('utf-8')
  
  from simplejson import *

  l = os.listdir(".")
  #l = [ "abcd" ]
  random.shuffle(l)
  a = bst(l)
  random.shuffle(l)
  je = JSONEncoder(ensure_ascii=False)
  jd = JSONDecoder()

  json = dumps(l, ensure_ascii = False)
  l1 = loads(json)

  for i in l1:
    print a.extract(i)
  print a.as_list()

