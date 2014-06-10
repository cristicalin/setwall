#!/usr/bin/env python
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

from urllib2 import quote, unquote
from threading import Lock

from gi.repository import Gio as gio
from gi.repository import GdkPixbuf as pixbuf
from gi.repository import Notify as notify

import globals

from utils import *

# This handles setting the wallpaper on the Gnome desktop
# and returning the name of the current wallpaper file
# This assumes that the current wallpaper is set
# if picture-uri in gsettings is null this will return None
class wallpapermanager:

  def __init__(self, my_settings):
    notify.init(globals.APP_NAME)
    self.notification = notify.Notification.new("", "", None)
    self.SETTINGS = my_settings
    self._LOCK = Lock()

  def get_wallpaper(self):
    try:
      old_wallpaper = self.SETTINGS.get_wallpaper()
      tmp = old_wallpaper.split("/")
      return unquote(tmp[-1])
    except:
      return None

  def get_wallpaper_full(self):
    try:
      old_wallpaper = self.SETTINGS.get_wallpaper()
      tmp = old_wallpaper.replace("file://", "")
      return unquote(tmp)
    except:
      return None

  def set_wallpaper(self, filename):
    with self._LOCK:
      old_wallpaper = self.get_wallpaper()
      new_file = filename.split("/")
      new_wallpaper = "file://%s" % quote(filename.encode("utf8"))
      self.SETTINGS.set_wallpaper(new_wallpaper)
      self.show_notification("Wallpaper changed",
                             "<b>Old:</b> %s\n<b>New:</b> %s" %
                             (shorten(old_wallpaper, 32),
                              shorten(new_file[-1], 32)),
                             new_wallpaper)

  def show_notification(self, title, message, filename):
    try:
      image_file = gio.File.new_for_uri(filename)
      resized_icon = pixbuf.Pixbuf.new_from_stream_at_scale(
        image_file.read(None), 
        64, 64, True, None
      )
      self.notification.set_icon_from_pixbuf(resized_icon)
      self.notification.update(title, message, None)
    except Exception as ex:
      self.notification.update(title, message, globals.APP_ICON)
    finally:
      self.notification.show()

if __name__ == "__main__":
  from settings import *
  s = settings()
  wpm = wallpapermanager(s)
  print wpm.get_wallpaper()
