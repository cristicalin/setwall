#!/usr/bin/python

from __future__ import division

import sys
import os

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf as pixbuf

import globals

# The settings class is a container for the application settings
# as well as a handler for the settings configuration window
class settings:

  # This inner class is used only to provide callbacks
  class handler:

    def __init__(self, settings):
      self.SETTINGS = settings

    def onApplyClicked(self, *args):
      self.SETTINGS.save()
      self.SETTINGS.hide_window()

    def onClose(self, *args):
      self.SETTINGS.hide_window()
      self.SETTINGS.APP.set_index()

    def onPathChanged(self, *args):
      self.SETTINGS.set_path(args[0].get_active_text())

    def onPrevious(self, *args):
      filename = "file://%s" % self.SETTINGS.APP.FILE_LIST.get_previous_file()
      self.SETTINGS.STATUS_BAR.push(0, filename)
      self.SETTINGS.show_preview(filename)

    def onNext(self, *args):
      filename = "file://%s" % self.SETTINGS.APP.FILE_LIST.get_next_file()
      self.SETTINGS.STATUS_BAR.push(0, filename)
      self.SETTINGS.show_preview(filename)

  def __init__(self, args = None, app = None):
    self.APP_SETTINGS = gio.Settings.new("%s.%s" % (globals.BASE_ID,
                                                    globals.APP_NAME.replace("_", "-")))
    self.APP = app
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
    self.STATUS_BAR = self.BUILDER.get_object("stStatus")
    self.WINDOW.set_title(globals.APP_FRIENDLY_NAME)
    window_icon = self.WINDOW.render_icon(gtk.STOCK_PREFERENCES,
                                          gtk.IconSize.DIALOG)
    self.WINDOW.set_icon(window_icon)

    self.ckSchedule = self.BUILDER.get_object("ckSchedule")
    self.ckLoadSavedList = self.BUILDER.get_object("ckLoadSavedList")
    self.spInterval = self.BUILDER.get_object("spInterval")
    self.cbPath = self.BUILDER.get_object("cbPath")
    self.imgPreview = self.BUILDER.get_object("imgPreview")

  def show_window(self):
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0]-50, 50)
    self.ckSchedule.set_active(self.get_wallpaper_schedule())
    self.ckLoadSavedList.set_active(self.get_wallpaper_save())
    self.spInterval.set_value(self.get_wallpaper_interval())
    self.set_path(self.get_wallpaper_path())
    filename = "file://%s" % self.APP.FILE_LIST.get_current_file()
    self.STATUS_BAR.push(0, filename)
    self.show_preview(filename)
    self.WINDOW.show_all()

  def show_preview(self, filename):
    image_file = gio.File.new_for_uri(filename)
    picture = pixbuf.Pixbuf.new_from_stream(image_file.read(None), None)
    scale = picture.get_width() / picture.get_height()
    preview_width = globals.PREVIEW_WIDTH
    preview_height = globals.PREVIEW_HEIGHT
    if scale < globals.PREVIEW_SCALE:
      preview_width = preview_height * scale
    else:
      preview_height = preview_width / scale
    preview = picture.scale_simple(preview_width, preview_height,
                                   pixbuf.InterpType.BILINEAR)
    self.imgPreview.set_from_pixbuf(preview)
    self.imgPreview.show()


  # We need to have the handlers blocked while we update the list
  def set_path(self, dirname):
    self.cbPath.handler_block_by_func(self.HANDLER.onPathChanged)
    self.cbPath.get_model().clear()
    names_list = os.listdir(dirname)
    names_list.sort()
    for name in names_list:
      path = os.path.join(dirname, name)
      if os.path.isdir(path) and not name.startswith("."):
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
    save = self.ckLoadSavedList.get_active()
    self.set_wallpaper_save(save)
    if self.APP is not None:
      self.APP.load_settings(True)

  def hide_window(self):
    self.WINDOW.hide()

  def get_window(self):
    return self.WINDOW

  def get_status_bar(self):
    return self.STATUS_BAR

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

  def get_wallpaper_save(self):
    return self.APP_SETTINGS.get_boolean(globals.WALLPAPER_SAVE)

  def set_wallpaper_save(self, wallpaper_save):
    self.APP_SETTINGS.set_boolean(globals.WALLPAPER_SAVE,
                                  wallpaper_save)

  def get_saved_list(self):
    return self.APP_SETTINGS.get_string(globals.WALLPAPER_SAVED_LIST)

  def set_saved_list(self, json):
    self.APP_SETTINGS.set_string(globals.WALLPAPER_SAVED_LIST, json)

  def get_wallpaper(self):
    return self.WALLPAPER_SETTINGS.get_string(globals.PICTURE_URI)

  def set_wallpaper(self, uri):
    self.WALLPAPER_SETTINGS.set_string(globals.PICTURE_URI, uri)

  def get_wallpaper_options_range(self):
    return self.WALLPAPER_SETTINGS.get_range(globals.PICTURE_OPTIONS)

  def get_wallpaper_options(self):
    return self.WALLPAPER_SETTINGS.get_string(globals.PICTURE_OPTIONS)

  def set_wallpaper_options(self, options):
    self.WALLPAPER_SETTINGS.set_string(globals.PICTURE_OPTIONS, options)

# for unit testing purposes only
if __name__ == "__main__":

  class callback:
    def load_settings(self, reload):
      print "callback(%d) called" % reload
      exit(0)

  s = settings(app = callback())
  print s.get_saved_list()
  s.show_window()
  
  #from json import JSONEncoder
  #j = JSONEncoder()
  #s.set_saved_list(j.encode([]))

  gtk.main()
