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

import dbus.service

import globals

# This is a handler class for the DBus messages, it allows
# the application to receive next and previous messages
class dbushandler(dbus.service.Object):

  def __init__(self, bus, app):
    self.APP = app
    dbus.service.Object.__init__(
      self, bus, "%s/%s" % (globals.APP_PATH, globals.APP_NAME)
    )

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def next(self):
    self.APP.next_wallpaper()

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                     in_signature='', out_signature='')
  def previous(self):
    self.APP.previous_wallpaper()

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def toggle(self):
    self.APP.toggle_schedule()

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def randomize(self):
    self.reorder_func(self.APP.FILE_LIST.randomize)

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def sort(self):
    self.reorder_func(self.APP.FILE_LIST.sort)

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def reverse(self):
    self.reorder_func(self.APP.FILE_LIST.reverse)

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def save(self):
    self.APP.save_json()

  @dbus.service.method("%s.%s" % (globals.BASE_ID, globals.APP_NAME),
                       in_signature='', out_signature='')
  def quit(self):
    self.APP.quit_app()

  def reorder_func(self, func):
    func()
    self.APP.set_index()
    self.APP.save_json()

# this is for unit testing only
if __name__ == "__main__":
  print "testing"