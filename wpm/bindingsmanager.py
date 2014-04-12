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

from gi.repository import Keybinder as keybinder

# this implements a generic key bindings manager
class bindingsmanager:

  def __init__(self):
    keybinder.init()
    self.BINDINGS = {}

  # remove a particular binding from our management
  def remove_binding(self, name):
    if self.BINDINGS.has_key(name):
      keybinder.unbind(self.BINDINGS[name]["key"])
      del self.BINDINGS[name]

  # set a particular binding, can also be used to update
  def set_binding(self, name, key, callback):
    # remove previous binding if it exists
    self.remove_binding(name)
    # create a new binding
    binding = {}
    binding["key"] = key
    binding["callback"] = callback
    ret = keybinder.bind(key, callback, None)
    self.BINDINGS[name] = binding
    return ret

  # check if a binding is usable or not for a new or existing combination
  def is_usable(self, name, key):
    for my_name in self.BINDINGS:
      if my_name == name and self.BINDINGS[my_name]["key"] == key:
        # if this is the same binding allow us to reuse it
        return True
      if self.BINDINGS[my_name]["key"] == key:
        # if this is used by some other binding disallow it
        return False
    # check if other binding are using this key combination
    if keybinder.bind(key, lambda *args: None, None):
      keybinder.unbind(key)
      return True
    else:
      return False

  # suspend all bindings, to be used to capture new bindings
  def suspend_bindings(self):
    for name in self.BINDINGS:
      keybinder.unbind(self.BINDINGS[name]["key"])

  # resume all bindings
  # return the number of resumed bindings
  def resume_bindings(self):
    count = 0
    for name in self.BINDINGS:
      count += keybinder.bind(
        self.BINDINGS[name]["key"], self.BINDINGS[name]["callback"], None
      )
    return count

if __name__ == "__main__":

  from gi.repository import Gtk
  
  def test_call1(*args):
    print "test_call1()"

  def quit(*args):
    print "quit()"
    Gtk.main_quit()

  bm = bindingsmanager()
  key_1 = "<Ctrl><Alt>1"
  key_quit = "<Ctrl><Alt>q"
  
  print bm.set_binding("key_1", key_1, test_call1)
  print bm.set_binding("quit", key_quit, quit)
  bm.suspend_bindings()
  print bm.is_usable("key_1", key_1)
  print bm.is_usable("key_1", key_quit)
  bm.resume_bindings()

  Gtk.main()