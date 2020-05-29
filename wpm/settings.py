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

import sys
import os
import copy
import threading

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import Gio as gio
from gi.repository import GObject as gobject
from gi.repository import GdkPixbuf as pixbuf

from .globals import global_constants

from .settingshandler import *
from .utils import *

# The settings class is a container for the application settings
# as well as a handler for the settings configuration window
class settings:

  def __init__(self, args = None, app = None):
    # These are Gnome specific settings for wallpaper and we need
    # a separate object to interact with them
    self.WALLPAPER_SETTINGS = gio.Settings.new(global_constants.WALLPAPER_SETTING)
    self.APP_SETTINGS = gio.Settings.new("%s.%s" % (global_constants.BASE_ID, global_constants.APP_SETTINGS))
    self.APP = app
    self.LOCAL_FILE_LIST = None
    self.PATH_LOCK = threading.Lock()
    # Store command line arguments in the settings for future reference
    # This means that if we want to change something we only need
    # to pass the correct command line value to the application one time
    if args is not None:
      if args.path != None:
        self.APP_SETTINGS.set_string(global_constants.WALLPAPER_PATH, args.path)
      if args.interval != None:
        self.APP_SETTINGS.set_int(global_constants.WALLPAPER_INTERVAL, args.interval)
      if args.schedule != None:
        self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_SCHEDULE, args.schedule)

    # Now build the windows and other Gtk objects
    self.BUILDER = gtk.Builder()
    try:
      self.BUILDER.add_from_file("%s/%s" % (os.path.dirname(sys.argv[0]),
                                            global_constants.GLADE_SETTINGS_FILE))
    except:
      self.BUILDER.add_from_file(global_constants.GLADE_SETTINGS_FILE)
    self.HANDLER = settingshandler(self)
    self.BUILDER.connect_signals(self.HANDLER)

    self.WINDOW = self.BUILDER.get_object("wcMain")
    self.STATUS_BAR = self.BUILDER.get_object("stStatus")
    self.WINDOW.set_title(global_constants.APP_FRIENDLY_NAME)
    window_icon = self.WINDOW.render_icon(gtk.STOCK_PREFERENCES,
                                          gtk.IconSize.DIALOG)
    self.WINDOW.set_icon(window_icon)

    self.ckRecursive = self.BUILDER.get_object("ckRecursive")
    self.ckSchedule = self.BUILDER.get_object("ckSchedule")
    self.ckLoadSavedList = self.BUILDER.get_object("ckLoadSavedList")
    self.ckReconcile = self.BUILDER.get_object("ckReconcile")
    self.ckVerifyPresence = self.BUILDER.get_object("ckVerifyPresence")
    self.ckVerifyImage = self.BUILDER.get_object("ckVerifyImage")
    self.ckOptimizeStoredLists = self.BUILDER.get_object("ckOptimizeStoredLists")
    self.spInterval = self.BUILDER.get_object("spInterval")
    self.cbPath = self.BUILDER.get_object("cbPath")
    self.imgPreview = self.BUILDER.get_object("imgPreview")

    self.tgNext = self.BUILDER.get_object("tgNext")
    self.tgPrevious = self.BUILDER.get_object("tgPrevious")
    self.tgFavorite = self.BUILDER.get_object("tgFavorite")

    self.toggles = []
    self.toggles.append([
      self.tgNext,
      self.get_next_key,
      self.set_next_key,
      global_constants.KEY_NEXT
    ])
    self.toggles.append([
      self.tgPrevious,
      self.get_previous_key,
      self.set_previous_key,
      global_constants.KEY_PREVIOUS
    ])
    self.toggles.append([
      self.tgFavorite,
      self.get_favorite_key,
      self.set_favorite_key,
      global_constants.KEY_FAVORITE
    ])

    for toggle in self.toggles:
      toggle[0].connect("toggled", self.HANDLER.onToggleKey, toggle[3])

  def show_window(self):
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0]-50, 50)
    self.ckRecursive.set_active(self.get_wallpaper_recursive())
    self.ckSchedule.set_active(self.get_wallpaper_schedule())
    self.ckLoadSavedList.set_active(self.get_wallpaper_save())
    self.ckReconcile.set_active(self.get_reconcile())
    self.ckVerifyPresence.set_active(self.get_verify_presence())
    self.ckVerifyImage.set_active(self.get_verify_image())
    self.ckOptimizeStoredLists.set_active(self.get_optimize_stored_lists())
    self.spInterval.set_value(self.get_wallpaper_interval())
    self.spInterval.set_sensitive(self.ckSchedule.get_active())
    for toggle in self.toggles:
      toggle[0].set_label(toggle[1]())
      toggle[0].set_active(False)
    self.LOCAL_FILE_LIST = copy.copy(self.APP.FILE_LIST)
    self.set_path(self.get_wallpaper_path(), False)
    filename = "file://%s" % self.LOCAL_FILE_LIST.get_current_file()
    self.STATUS_BAR.push(0, filename)
    self.show_preview(filename)
    self.WINDOW.show_all()

  # Show a scaled down preview of a image
  def show_preview(self, filename):
    try:
      image_file = gio.File.new_for_uri(filename)
      # size request is set on the container box which holds the Viewport
      container = self.imgPreview.get_parent()
      width, height = container.get_size_request()
      preview = pixbuf.Pixbuf.new_from_stream_at_scale(
        image_file.read(None), width, height, True, None
      )
      self.imgPreview.set_from_pixbuf(preview)
    except Exception as e:
      print(e)
      self.imgPreview.set_from_stock(gtk.STOCK_FILE, gtk.IconSize.DIALOG)
    finally:
      self.imgPreview.show()

  # We need to have the handlers blocked while we update the list
  def _set_path(self, dirname, changed):
    self.PATH_LOCK.acquire()
    temp_list = []
    position = 0
    try:
      # put children first
      names_list = get_dir_list(dirname)
      names_list.sort()
      temp_list = []
      for name in names_list:
        path = os.path.join(dirname, name)
        temp_list.append(path)
      # then append the actual folder
      temp_list.append(dirname)
      # then append the list of parent folders
      self.build_path(dirname, temp_list)
      position = temp_list.index(dirname)
      if changed:
        self.LOCAL_FILE_LIST.load_from_path(dirname)
        self.LOCAL_FILE_LIST.sort()
    finally:
      gobject.idle_add(self.update_cb_path, temp_list, position)      
    self.PATH_LOCK.release()

  # Set Path may be slow so we want to execute it in a separate thread
  def set_path(self, dirname, changed = False):
    self.cbPath.handler_block_by_func(self.HANDLER.onPathChanged)
    # initially set only the current path
    self.update_cb_path([dirname], 0)
    # disable path change handler again
    self.cbPath.handler_block_by_func(self.HANDLER.onPathChanged)
    # then spin up a thread to populate the rest
    # we do this in a thread to defer the loading and
    # allow the settings dialog to load faster
    thread = threading.Thread(target = self._set_path, args = (dirname, changed))
    thread.start()

  # Update the GUI element cbPath
  def update_cb_path(self, my_list, position):
    model = self.cbPath.get_model()
    model.clear()
    for i in my_list:
      model.append([i, None])
    self.cbPath.set_active(position)
    self.cbPath.handler_unblock_by_func(self.HANDLER.onPathChanged)

  # recursively build the down path
  def build_path(self, path, my_list):
    if len(path)>1:
      d = os.path.dirname(path)
      my_list.append(d)
      self.build_path(d, my_list)

  # save the settings
  def save(self):
    path = self.cbPath.get_active_text()
    if (os.path.isdir(path)):
      self.set_wallpaper_path(path)
    self.set_wallpaper_interval(self.spInterval.get_value())
    self.set_wallpaper_recursive(self.ckRecursive.get_active())
    self.set_wallpaper_schedule(self.ckSchedule.get_active())
    self.set_wallpaper_save(self.ckLoadSavedList.get_active())
    self.set_reconcile(self.ckReconcile.get_active())
    self.set_verify_presence(self.ckVerifyPresence.get_active())
    self.set_verify_image(self.ckVerifyImage.get_active())
    if self.get_optimize_stored_lists() != self.ckOptimizeStoredLists.get_active():
      tmp_saved_list = self.get_saved_list()
      tmp_favorites = self.get_favorites()
      self.set_optimize_stored_lists(self.ckOptimizeStoredLists.get_active())
      self.set_saved_list(tmp_saved_list)
      self.set_favorites(tmp_favorites)
    for toggle in self.toggles:
      toggle[2](toggle[0].get_label())
    if self.APP is not None:
      self.APP.load_settings(True, self.LOCAL_FILE_LIST)

  def hide_window(self):
    if self.LOCAL_FILE_LIST is not None:
      self.LOCAL_FILE_LIST.close()
    self.HANDLER.disconnect(True)
    self.WINDOW.hide()

  def flip_toggles(self, toggle):
    for i in self.toggles:
      if i[0] != toggle:
        i[0].handler_block_by_func(self.HANDLER.onToggleKey)
        i[0].set_active(False)
        i[0].handler_unblock_by_func(self.HANDLER.onToggleKey)

  def get_window(self):
    return self.WINDOW

  def get_status_bar(self):
    return self.STATUS_BAR

  def get_builder(self):
    return self.BUILDER

  def _set_list(self, settings_path, my_list):
    if self.get_optimize_stored_lists():
      value = encode_list(my_list)
    else:
      value = to_json(my_list)
    self.APP_SETTINGS.set_string(settings_path, value)

  def _get_list(self, settings_path):
    value = self.APP_SETTINGS.get_string(settings_path)
    if self.get_optimize_stored_lists():
      return decode_list(value)
    else:
      return from_json(value)

  def get_wallpaper_path(self):
    return self.APP_SETTINGS.get_string(global_constants.WALLPAPER_PATH)

  def set_wallpaper_path(self, wallpaper_path):
    self.APP_SETTINGS.set_string(global_constants.WALLPAPER_PATH,
                                 wallpaper_path)

  def get_wallpaper_recursive(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_RECURSIVE)

  def set_wallpaper_recursive(self, wallpaper_recursive):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_RECURSIVE,
                                  wallpaper_recursive)

  def get_wallpaper_interval(self):
    return self.APP_SETTINGS.get_int(global_constants.WALLPAPER_INTERVAL)

  def set_wallpaper_interval(self, wallpaper_interval):
    self.APP_SETTINGS.set_int(global_constants.WALLPAPER_INTERVAL,
                              wallpaper_interval)

  def get_wallpaper_schedule(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_SCHEDULE)

  def set_wallpaper_schedule(self, wallpaper_schedule):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_SCHEDULE,
                                  wallpaper_schedule)

  def get_wallpaper_save(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_SAVE)

  def set_wallpaper_save(self, wallpaper_save):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_SAVE,
                                  wallpaper_save)

  def get_saved_list(self):
    #return self.APP_SETTINGS.get_string(global_constants.WALLPAPER_SAVED_LIST)
    return self._get_list(global_constants.WALLPAPER_SAVED_LIST)

  def set_saved_list(self, the_list):
    #self.APP_SETTINGS.set_string(global_constants.WALLPAPER_SAVED_LIST, json)
    self._set_list(global_constants.WALLPAPER_SAVED_LIST, the_list)

  def get_reconcile(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_RECONCILE)

  def set_reconcile(self, reconcile):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_RECONCILE, reconcile)

  def get_verify_presence(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_VERIFY_PRESENCE)

  def set_verify_presence(self, verify_presence):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_VERIFY_PRESENCE,
                                  verify_presence)

  def get_verify_image(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_VERIFY_IMAGE)

  def set_verify_image(self, verify_image):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_VERIFY_IMAGE,
                                  verify_image)

  def get_wallpaper(self):
    return self.WALLPAPER_SETTINGS.get_string(global_constants.PICTURE_URI)

  def set_wallpaper(self, uri):
    self.WALLPAPER_SETTINGS.set_string(global_constants.PICTURE_URI, uri)

  def get_wallpaper_options_range(self):
    return self.WALLPAPER_SETTINGS.get_range(global_constants.PICTURE_OPTIONS)

  def get_wallpaper_options(self):
    return self.WALLPAPER_SETTINGS.get_string(global_constants.PICTURE_OPTIONS)

  def set_wallpaper_options(self, options):
    self.WALLPAPER_SETTINGS.set_string(global_constants.PICTURE_OPTIONS, options)

  def get_favorites(self):
    #return self.APP_SETTINGS.get_string(global_constants.WALLPAPER_FAVORITES)
    return self._get_list(global_constants.WALLPAPER_FAVORITES)

  def set_favorites(self, favorites):
    #self.APP_SETTINGS.set_string(global_constants.WALLPAPER_FAVORITES, favorites)
    self._set_list(global_constants.WALLPAPER_FAVORITES, favorites)

  def get_next_key(self):
    return self.APP_SETTINGS.get_string(global_constants.KEY_NEXT)

  def set_next_key(self, key):
    self.APP_SETTINGS.set_string(global_constants.KEY_NEXT, key)

  def get_previous_key(self):
    return self.APP_SETTINGS.get_string(global_constants.KEY_PREVIOUS)

  def set_previous_key(self, key):
    self.APP_SETTINGS.set_string(global_constants.KEY_PREVIOUS, key)

  def get_favorite_key(self):
    return self.APP_SETTINGS.get_string(global_constants.KEY_FAVORITE)

  def set_favorite_key(self, key):
    self.APP_SETTINGS.set_string(global_constants.KEY_FAVORITE, key)

  def get_current_favorite_list(self):
    return self.APP_SETTINGS.get_string(global_constants.WALLPAPER_CURRENT_FAVORITE)

  def set_current_favorite_list(self, list):
    self.APP_SETTINGS.set_string(global_constants.WALLPAPER_CURRENT_FAVORITE, list)

  def get_optimize_stored_lists(self):
    return self.APP_SETTINGS.get_boolean(global_constants.WALLPAPER_OPTIMIZE_STORED_LISTS)

  def set_optimize_stored_lists(self, key):
    self.APP_SETTINGS.set_boolean(global_constants.WALLPAPER_OPTIMIZE_STORED_LISTS, key)

# for unit testing purposes only
if __name__ == "__main__":

  class callback:
    def load_settings(self, reload):
      print("callback(%d) called" % reload)
      exit(0)

  s = settings(app = callback())
  print(s.get_saved_list())
  s.show_window()
  
  #from json import JSONEncoder
  #j = JSONEncoder()
  #s.set_saved_list(j.encode([]))

  gtk.main()
