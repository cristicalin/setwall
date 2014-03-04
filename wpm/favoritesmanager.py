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

from utils import *

class favoritesmanager():

  def __init__(self, app):
    self.APP = app
    self.SETTINGS = app.SETTINGS
    self.FAVORITES = from_json(self.SETTINGS.get_favorites())
    self.NEED_SAVE = False

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

  def get_favorites(self):
    return self.FAVORITES

  def get_json(self):
    return to_json(self.FAVORITES)

  def get_need_save(self):
    return self.NEED_SAVE


# this is for unit testing only
if __name__ == "__main__":
  fm = favoritesmanager()