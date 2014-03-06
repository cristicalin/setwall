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

from os.path import *
from simplejson import *

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

import globals

from utils import *

class favoritesmanager():

  # This inner class is used only to provide callbacks
  class handler:

    def __init__(self, favorites):
      self.FAVORITES = favorites

    def onSaveClicked(self, *args):
      print "onSaveClicked() not yet implemented"

    def onCloseClicked(self, *args):
      self.FAVORITES.hide_window()

  def __init__(self, app):
    self.APP = app
    self.SETTINGS = app.SETTINGS
    self.FAVORITES = from_json(self.SETTINGS.get_favorites())
    self.NEED_SAVE = False
    self.BUILDER = gtk.Builder()
    try:
      self.BUILDER.add_from_file("%s/%s" % (os.path.dirname(sys.argv[0]),
                                            globals.GLADE_FAVORTIES_FILE))
    except:
      self.BUILDER.add_from_file(globals.GLADE_FAVORITES_FILE)
    self.HANDLER = self.handler(self)
    self.BUILDER.connect_signals(self.HANDLER)

    self.WINDOW = self.BUILDER.get_object("wcFavorites")
    self.TREE_STORE = self.BUILDER.get_object("tsFavorites")
    self.TREE_VIEW = self.BUILDER.get_object("tvFavorites")
    column = gtk.TreeViewColumn("Favorite List")
    self.TREE_VIEW.append_column(column)
    cell = gtk.CellRendererText()
    column.pack_start(cell, False)
    column.add_attribute(cell, "text", 0)
    self.WINDOW.set_title("%s Favorites" % globals.APP_FRIENDLY_NAME)
    window_icon = self.WINDOW.render_icon(gtk.STOCK_DIALOG_INFO,
                                          gtk.IconSize.DIALOG)
    self.WINDOW.set_icon(window_icon)


  # add a new entry to the favorites list
  # favorites list is a map of arrays, map key is the folder name
  # arrays contain the file names
  def add_favorite(self, current):
    folder = dirname(current)
    filename = basename(current)

    if folder in self.FAVORITES:
      # only add file if not already present
      if not filename in self.FAVORITES[folder]:
        self.FAVORITES[folder].append(filename)
        self.NEED_SAVE = True
    else:
      self.FAVORITES[folder] = [filename]
      self.NEED_SAVE = True

    self.APP.MENU_OBJECT.append_favorite(folder, filename)

  # Show the favorites window
  def show_window(self):
    self.WINDOW.move(gdk.Screen.width()-self.WINDOW.get_size()[0]-50, 50)
    self.TREE_STORE.clear()
    for folder in self.FAVORITES:
      folder_tree = self.TREE_STORE.append(None, [folder])
      for filename in self.FAVORITES[folder]:
        self.TREE_STORE.append(folder_tree, [filename])
    self.WINDOW.show_all()

  def hide_window(self):
    self.WINDOW.hide()

  def get_favorites(self):
    return self.FAVORITES

  def get_json(self):
    return to_json(self.FAVORITES)

  def get_need_save(self):
    return self.NEED_SAVE


# this is for unit testing only
if __name__ == "__main__":
  fm = favoritesmanager()