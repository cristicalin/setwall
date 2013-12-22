#!/usr/bin/python

import sys
import os
import re

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
      self.settings.save()
      self.settings.hide_window()

    def onClose(self, *args):
      self.settings.hide_window()

    def onPathChanged(self, *args):
      self.settings.set_path(args[0].get_active_text())

  def __init__(self, args = None, save_callback = None):
    self.APP_SETTINGS = gio.Settings.new("%s.%s" % (globals.BASE_ID,
                                                    globals.APP_NAME.replace("_", "-")))
    # Store command line arguments in the settings for future reference
    # This means that if we want to change something we only need
    # to pass the correct command line value to the application one time
    if args is not None:
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
    self.HANDLER = self.handler(self)
    self.BUILDER.connect_signals(self.HANDLER)

    self.WINDOW = self.BUILDER.get_object("wcMain")
    self.WINDOW.set_title(" ".join([word.capitalize() 
                          for word in globals.APP_NAME.split("_")]))
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0], 0)

    self.SAVE_CALLBACK = save_callback
    self.ckSchedule = self.BUILDER.get_object("ckSchedule")
    self.spInterval = self.BUILDER.get_object("spInterval")
    self.cbPath = self.BUILDER.get_object("cbPath")

  def show_window(self):
    self.ckSchedule.set_active(self.get_wallpaper_schedule())
    self.spInterval.set_value(self.get_wallpaper_interval())
    self.set_path(self.get_wallpaper_path())
    self.WINDOW.show_all()

  # We need to have the handlers blocked while we update the list
  def set_path(self, dirname):
    self.cbPath.handler_block_by_func(self.HANDLER.onPathChanged)
    self.cbPath.get_model().clear()
    names_list = os.listdir(dirname)
    names_list.sort()
    for name in names_list:
      path = os.path.join(dirname, name)
      if os.path.isdir(path) and re.search('^\.', name) is None:
        self.cbPath.append_text(path)
    position = len(self.cbPath.get_model())
    self.cbPath.append_text(dirname)
    self.build_path(dirname)
    self.cbPath.set_active(position)
    self.cbPath.handler_unblock_by_func(self.HANDLER.onPathChanged)

  # recursively build the down path
  def build_path(self, path):
    if len(path)>1:
      d = os.path.dirname(path)
      self.cbPath.append_text(d)
      self.build_path(d)

  # save the settings
  def save(self):
    path = self.cbPath.get_active_text()
    if (os.path.isdir(path)):
      self.set_wallpaper_path(path)
    interval = self.spInterval.get_value()
    self.set_wallpaper_interval(interval)
    schedule = self.ckSchedule.get_active()
    self.set_wallpaper_schedule(schedule)
    if self.SAVE_CALLBACK is not None:
      self.SAVE_CALLBACK()

  def hide_window(self):
    self.WINDOW.hide()

  def get_window(self):
    return self.WINDOW

  def get_builder(self):
    return self.BUILDER

  def get_wallpaper_path(self):
    return self.APP_SETTINGS.get_string(globals.WALLPAPER_PATH)

  def set_wallpaper_path(self, wallpaper_path):
    self.APP_SETTINGS.set_string(globals.WALLPAPER_PATH,
                                 wallpaper_path)

  def get_wallpaper_interval(self):
    return self.APP_SETTINGS.get_int(globals.WALLPAPER_INTERVAL)

  def set_wallpaper_interval(self, wallpaper_interval):
    self.APP_SETTINGS.set_int(globals.WALLPAPER_INTERVAL,
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

  def callback():
    print "callback() called"
    exit(0)

  s = settings(save_callback = callback)
  s.show_window()

  gtk.main()
