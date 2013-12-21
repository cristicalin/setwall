#!/usr/bin/python

import sys
import os

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import Gio as gio

import globals

# The settings class is a container for the application settings
# as well as a handler for the settings configuration window
class settings:

  # This inner class is used only to provide callbacks
  class handler:

    def __init__(self, settings):
      self.settings = settings

    def onApplyClicked(self, *args):
      self.settings.hide_window()

    def onClose(self, *args):
      self.settings.hide_window()

  def __init__(self, args):
    self.APP_SETTINGS = gio.Settings.new("%s.%s" % (globals.BASE_ID,
                                                    globals.APP_NAME.replace("_", "-")))
    # Store command line arguments in the settings for future reference
    # This means that if we want to change something we only need
    # to pass the correct command line value to the application one time
    if args.path != None:
      self.APP_SETTINGS.set_string(globals.WALLPAPER_PATH, args.path)
    if args.interval != None:
      self.APP_SETTINGS.set_int(globals.WALLPAPER_INTERVAL, args.interval)
    if args.schedule != None:
      self.APP_SETTINGS.set_boolean(globals.WALLPAPER_SCHEDULE, args.schedule)

    # These are Gnome specific settings for wallpaper and we need
    # a separate object to interact with them
    self.WALLPAPER_SETTINGS = gio.Settings.new(globals.WALLPAPER_SETTING)

    # Now build the windows and other Gtk objects
    self.BUILDER = gtk.Builder()
    try:
      self.BUILDER.add_from_file("%s/%s" % (os.path.dirname(sys.argv[0]),
                                            globals.GLADE_FILE))
    except:
      self.BUILDER.add_from_file(globals.GLADE_FILE)
    self.BUILDER.connect_signals(self.handler(self))

    self.WINDOW = self.BUILDER.get_object("wcMain")
    self.WINDOW.set_title(" ".join([word.capitalize() 
                          for word in globals.APP_NAME.split("_")]))
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0], 0)

  def show_window(self):
    self.WINDOW.show_all()

  def hide_window(self):
    self.WINDOW.hide()

  def get_window(self):
    return self.WINDOW

  def get_wallpaper_path(self):
    return self.APP_SETTINGS.get_string(globals.WALLPAPER_PATH)

  def set_wallpaper_path(self, wallpaper_path):
    self.APP_SETTINGS.set_string(globals.WALLPAPER_PATH,
                                 wallpaper_path)

  def get_wallpaper_interval(self):
    return self.APP_SETTINGS.get_int(globals.WALLPAPER_INTERVAL)

  def set_wallpaper_interval(self, wallpaper_interval):
    self.APP_SETTINGS.get_int(globals.WALLPAPER_INTERVAL,
                              wallpaper_interval)

  def get_wallpaper_schedule(self):
    return self.APP_SETTINGS.get_boolean(globals.WALLPAPER_SCHEDULE)

  def set_wallpaper_schedule(self, wallpaper_schedule):
    self.APP_SETTINGS.set_boolean(globals.WALLPAPER_SCHEDULE,
                                  wallpaper_schedule)

  def get_wallpaper(self):
    return self.WALLPAPER_SETTINGS.get_string(globals.PICTURE_URI)

  def set_wallpaper(self, uri):
    self.WALLPAPER_SETTINGS.set_string(globals.PICTURE_URI, uri)

  def get_wallpaper_options_range(self):
    return self.WALLPAPER_SETTINGS.get_range(globals.PICTURE_OPTIONS)

  def set_wallpaper_options(self, options):
    self.WALLPAPER_SETTINGS.set_string(globals.PICTURE_OPTIONS, options)


# for unit testing purposes only
if __name__ == "__main__":

  s = settings()
  s.show_window()

  gtk.main()
