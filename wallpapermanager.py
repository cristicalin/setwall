#!/usr/bin/python

from __future__ import division

from urllib2 import quote, unquote

from gi.repository import Gio as gio
from gi.repository import GdkPixbuf as pixbuf
from gi.repository import Notify as notify

# Local imports
from globals import *
from settings import *

# This handles setting the wallpaper on the Gnome desktop
# and returning the name of the current wallpaper file
# This assumes that the current wallpaper is set
# if picture-uri in gsettings is null this will return None
class wallpapermanager:

  def __init__(self, my_settings):
    self.notification = notify.Notification.new("", "", None)
    self.SETTINGS = my_settings

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
    old_wallpaper = self.get_wallpaper()
    new_file = filename.split("/")
    new_wallpaper = "file://%s" % quote(filename)
    self.SETTINGS.set_wallpaper(new_wallpaper)
    self.show_notification("Wallpaper changed",
                           "<b>Old:</b> %s<br/><b>New:</b> %s" %
                           (shorten(old_wallpaper, 32),
			    shorten(new_file[-1], 32)),
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
  s = settings()
  wpm = wallpapermanager(s)
  print wpm.get_wallpaper()
