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

from __future__ import division

import sys
import os.path

from os.path import *
from simplejson import *

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import Gio as gio
from gi.repository import GdkPixbuf as pixbuf

import globals

from favoriteshandler import *
from utils import *

class favoritesmanager():

  def __init__(self, app):
    self.APP = app
    self.SETTINGS = app.SETTINGS
    self.FAVORITES_LIST = from_json(self.SETTINGS.get_favorites())
    self.NEED_SAVE = False
    self.BUILDER = gtk.Builder()
    try:
      self.BUILDER.add_from_file("%s/%s" % (os.path.dirname(sys.argv[0]),
                                            globals.GLADE_FAVORITES_FILE))
    except:
      self.BUILDER.add_from_file(globals.GLADE_FAVORITES_FILE)
    self.HANDLER = favoriteshandler(self)
    self.BUILDER.connect_signals(self.HANDLER)

    self.WINDOW = self.BUILDER.get_object("wcFavorites")
    self.PREVIEW = self.BUILDER.get_object("imgPreview")
    self.PREVIEW_SCROLL = self.BUILDER.get_object("scrPreview")
    self.PREVIEW_BUFFER = None
    self.TREE_STORE = self.BUILDER.get_object("tsFavorites")
    self.TREE_VIEW = self.BUILDER.get_object("tvFavorites")
    self.PREVIEW_H_ADJUSTMENT = self.BUILDER.get_object("adjPreviewHorizontal")
    self.PREVIEW_V_ADJUSTMENT = self.BUILDER.get_object("adjPreviewVertical")
    column = gtk.TreeViewColumn("Favorite List")
    self.TREE_VIEW.append_column(column)
    cell = gtk.CellRendererText()
    column.pack_start(cell, False)
    column.add_attribute(cell, "text", 0)
    self.STATUS_BAR = self.BUILDER.get_object("stBar")
    self.WINDOW.set_title("%s Favorites" % globals.APP_FRIENDLY_NAME)
    window_icon = self.WINDOW.render_icon(gtk.STOCK_DIALOG_INFO,
                                          gtk.IconSize.DIALOG)
    self.WINDOW.set_icon(window_icon)
    self.ZOOMED = False

  # add a new entry to the favorites list
  # favorites list is a map of arrays, map key is the folder name
  # arrays contain the file names
  def add_favorite(self, current):
    folder = dirname(current)
    filename = basename(current)

    if folder in self.FAVORITES_LIST:
      # only add file if not already present
      if not filename in self.FAVORITES_LIST[folder]:
        self.FAVORITES_LIST[folder].append(filename)
        self.NEED_SAVE = True
    else:
      self.FAVORITES_LIST[folder] = [filename]
      self.NEED_SAVE = True

    self.APP.MENU_OBJECT.append_favorite(folder, filename)

  # Show the favorites window
  def show_window(self):
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0]-50, 50)
    self.TREE_STORE.clear()
    for folder in self.FAVORITES_LIST:
      folder_tree = self.TREE_STORE.append(None, [folder])
      for filename in self.FAVORITES_LIST[folder]:
        self.TREE_STORE.append(folder_tree, [filename])
    self.PREVIEW.set_from_stock(gtk.STOCK_FILE, gtk.IconSize.DIALOG)
    self.STATUS_BAR.push(0, "Unknown")
    self.WINDOW.show_all()

  # Show a preview of the picture in the preview window
  def show_preview(self, folder, filename):
    try:
      image_file = gio.File.new_for_uri("file://%s/%s" % (folder, filename))
      self.PREVIEW_BUFFER = pixbuf.Pixbuf.new_from_stream(
        image_file.read(None), None
      )
      self.STATUS_BAR.push(0, "%s (%dx%d)" % (
        filename,
        self.PREVIEW_BUFFER.get_width(),
        self.PREVIEW_BUFFER.get_height()
      ))
      self.ZOOMED = True
      self.display_zoomed_out_image()
    except Exception as e:
      print e
      self.PREVIEW.set_from_stock(gtk.STOCK_FILE, gtk.IconSize.DIALOG)
      self.STATUS_BAR.push(0, "Unknown")
      self.PREVIEW.show()

  # scale the image down to the size of the view pane
  # fill the entire view pane and allow extra to scroll if needed
  def display_zoomed_out_image(self):
    if self.ZOOMED:
      image_width = self.PREVIEW_BUFFER.get_width()
      image_height = self.PREVIEW_BUFFER.get_height()
      width = self.PREVIEW_SCROLL.get_allocated_width()
      height = self.PREVIEW_SCROLL.get_allocated_height()
      scroll_ratio = width / height
      image_ratio = image_width / image_height
      if image_ratio > scroll_ratio:
        width = height * image_ratio
      else:
        height = width / image_ratio
      self.PREVIEW.set_from_pixbuf(
        self.PREVIEW_BUFFER.scale_simple(
          width, 
          height, 
          pixbuf.InterpType.BILINEAR
        )
      )
      self.PREVIEW.show()
      self.ZOOMED = False
      self.set_adjustments(0, 0)

  # display the image on a 1:1 ratio
  def display_zoomed_in_image(self):
    if not self.ZOOMED:
      self.PREVIEW.set_from_pixbuf(self.PREVIEW_BUFFER)
      self.PREVIEW.show()
      self.ZOOMED = True
      self.set_adjustments(0, 0)

  # manage adjustments for preview window
  def get_adjustments(self):
    adj_x = self.PREVIEW_H_ADJUSTMENT.get_value()
    adj_y = self.PREVIEW_V_ADJUSTMENT.get_value()
    return adj_x, adj_y

  def set_adjustments(self, adj_x, adj_y):
    self.PREVIEW_H_ADJUSTMENT.set_value(adj_x)
    self.PREVIEW_V_ADJUSTMENT.set_value(adj_y)

  # this function assumes there are only two levels in the tree
  def walk_map(self, model, path, iter, mapptr):
    parent = model.iter_parent(iter)
    obj = model[iter][0]
    if parent is None:
      mapptr[obj] = []
    else:
      parent_name = model[parent][0]
      mapptr[parent_name].append(obj) 
  
  def save_favorites(self):
    tmp_map = {}
    self.TREE_STORE.foreach(self.walk_map, tmp_map)
    self.FAVORITES_LIST = tmp_map
    self.set_need_save(True)
    self.APP.save_json()
    self.APP.MENU_OBJECT.update_favorites()
    
  def hide_window(self):
    self.WINDOW.hide()

  def get_favorites(self):
    return self.FAVORITES_LIST

  def get_json(self):
    return to_json(self.FAVORITES_LIST)

  def get_need_save(self):
    return self.NEED_SAVE

  def set_need_save(self, value):
    self.NEED_SAVE = value


# this is for unit testing only
if __name__ == "__main__":
  fm = favoritesmanager()