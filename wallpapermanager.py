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

# we need to support real division instead of
# integer which is the Python default division
from __future__ import division

from urllib2 import quote, unquote
from threading import Lock

from gi.repository import Gio as gio
from gi.repository import GdkPixbuf as pixbuf
from gi.repository import Notify as notify

import globals

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

  # Shorten long file names
  def shorten(self, data, length):
    info = (data[:int(length/2)-1] + '..' + 
            data[-(int(length/2)-1):]) if len(data) > length else data
    return info

  def get_wallpaper(self):
    try:
      old_wallpaper = self.SETTINGS.get_wallpaper()
      tmp = old_wallpaper.split("/")
      return unquote(tmp[-1])
    except:
      return None

  def set_wallpaper(self, filename):
    with self._LOCK:
      old_wallpaper = self.get_wallpaper()
      new_file = filename.split("/")
      new_wallpaper = "file://%s" % quote(filename)
      self.SETTINGS.set_wallpaper(new_wallpaper)
      self.show_notification("Wallpaper changed",
                             "<b>Old:</b> %s<br/><b>New:</b> %s" %
                             (self.shorten(old_wallpaper, 32),
  			                      self.shorten(new_file[-1], 32)),
  			                     new_wallpaper)

  def show_notification(self, title, message, filename):
    if filename is not None:
      file = gio.File.new_for_uri(filename)
      icon = pixbuf.Pixbuf.new_from_stream(file.read(None), None)
      scale = icon.get_width() / icon.get_height()
      resized_icon = icon.scale_simple(64, 64/scale,
                                       pixbuf.InterpType.BILINEAR)
      self.notification.set_icon_from_pixbuf(resized_icon)
      self.notification.update(title, message, None)
    else:
      self.notification.update(title, message, globals.APP_ICON)
    self.notification.show()

if __name__ == "__main__":
  from settings import *
  s = settings()
  wpm = wallpapermanager(s)
  print wpm.get_wallpaper()
