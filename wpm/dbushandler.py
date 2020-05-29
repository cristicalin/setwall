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

import dbus
import dbus.glib
import dbus.service

from .globals import global_constants

# This is a handler class for the DBus messages, it allows
# the application to receive next and previous messages
class dbushandler(dbus.service.Object):

  def __init__(self, app):
    self.APP = app
    self.SESSION_BUS = dbus.SessionBus()

    # we need to kill the previous instance as a first thing
    try:
      running_obj = self.SESSION_BUS.get_object(
        "%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
        "%s/%s" % (global_constants.APP_PATH, global_constants.APP_NAME)
      )
      running_obj.quit()
    except dbus.DBusException as e:
      None
    self.SESSION_NAME = dbus.service.BusName(
      "%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME), self.SESSION_BUS
    )
    dbus.service.Object.__init__(
      self, self.SESSION_BUS, "%s/%s" % (global_constants.APP_PATH, global_constants.APP_NAME)
    )
    self.SESSION_BUS.add_signal_receiver(
      self.screen_saver_handler,
      dbus_interface = global_constants.SCREEN_SAVER_NAME,
      signal_name = global_constants.SCREEN_SAVER_SIGNAL
    )

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='s', out_signature='')
  def set(self, wallpaper):
    self.APP.set_wallpaper(wallpaper)

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='s')
  def next(self):
    return self.APP.next_wallpaper()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                     in_signature='', out_signature='s')
  def previous(self):
    return self.APP.previous_wallpaper()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                     in_signature='', out_signature='s')
  def get(self):
    return self.APP.FILE_LIST.get_current_file()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def toggle(self):
    self.APP.toggle()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def randomize(self):
    self.reorder_func(self.APP.FILE_LIST.randomize)

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def sort(self):
    self.reorder_func(self.APP.FILE_LIST.sort)

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def reverse(self):
    self.reorder_func(self.APP.FILE_LIST.reverse)

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def favorite(self):
    self.APP.add_current_to_favorites()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def save(self):
    self.APP.save_lists()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def reconcile(self):
    self.APP.reconcile()

  @dbus.service.method("%s.%s" % (global_constants.BASE_ID, global_constants.APP_NAME),
                       in_signature='', out_signature='')
  def quit(self):
    self.APP.quit_app()

  def reorder_func(self, func):
    func()
    self.APP.set_index()
    self.APP.save_lists()

  # suspend schedule while screen saver / lock is in place
  def screen_saver_handler(self, active):
    if active:
      self.APP.suspend_schedule()
    else:
      self.APP.resume_schedule()

# this is for unit testing only
if __name__ == "__main__":
  print("testing")
