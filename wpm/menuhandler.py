#!/usr/bin/env python3
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

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

from .globals import global_constants

# Manage setwall application menu
class menuhandler():

  def __init__(self, app):
    self.FAVORITES_TOGGLES = []
    self.APP = app
    self.SETTINGS = app.SETTINGS
    self.INDICATOR = appindicator.Indicator.new(
      global_constants.APP_SETTINGS, global_constants.APP_ICON,
      appindicator.IndicatorCategory.APPLICATION_STATUS
    )
    self.INDICATOR.set_status(appindicator.IndicatorStatus.ACTIVE)
    self.MAIN_MENU = self.get_app_menu()
    self.INDICATOR.set_menu(self.MAIN_MENU)

  # Build the application menu which is delivered
  # via the appindicator functionality
  def get_app_menu(self):
    menu = gtk.Menu()
   
    next_menu = gtk.MenuItem()
    next_menu.set_label("Next")
    next_menu.connect("activate", self.APP.next_wallpaper)
    menu.append(next_menu)

    prev_menu = gtk.MenuItem()
    prev_menu.set_label("Previous")
    prev_menu.connect("activate", self.APP.previous_wallpaper)
    menu.append(prev_menu)

    options_menu_item = gtk.MenuItem()
    options_menu_item.set_label("Options");
    menu.append(options_menu_item)
    options_menu_item.set_submenu(self.build_options_menu())

    favorites_menu_item = gtk.MenuItem()
    favorites_menu_item.set_label("Favorites");
    menu.append(favorites_menu_item)
    favorites_menu_item.set_submenu(self.build_favorites_menu())
    self.FAVORITES_MENU = favorites_menu_item
    
    slideshow_menu = gtk.CheckMenuItem()
    slideshow_menu.set_label("Slideshow")
    handler = slideshow_menu.connect("toggled", self.APP.toggle)
    slideshow_menu.handler_block(handler)
    slideshow_menu.set_active(self.SETTINGS.get_wallpaper_schedule())
    slideshow_menu.handler_unblock(handler)
    menu.append(slideshow_menu)
    self.SLIDESHOW = slideshow_menu

    menu.append(gtk.SeparatorMenuItem())

    settings_menu = gtk.MenuItem()
    settings_menu.set_label("Settings")
    settings_menu.connect("activate", self.APP.show_settings)
    menu.append(settings_menu)

    quit_menu = gtk.MenuItem()
    quit_menu.set_label("Quit")
    quit_menu.connect("activate", self.APP.quit_app)
    menu.append(quit_menu)

    menu.show_all()
    return menu

  # Build options submenu
  def build_options_menu(self):
    options_menu = gtk.Menu()

    options_range = self.SETTINGS.get_wallpaper_options_range()
    options_group = []
    # avoid calling get_wallpaper_options() multiple times
    tmp_wp_options = self.SETTINGS.get_wallpaper_options()
    for option in options_range[1]:
      menu_option = gtk.RadioMenuItem.new_with_label(
        options_group,
        option.title()
      )
      menu_option.connect(
        "activate", self.set_wallpaper_options, option
      )
      if option == tmp_wp_options:
        menu_option.set_active(True)
      options_group = menu_option.get_group()
      options_menu.append(menu_option)

    return options_menu

  # Set wallpaper options
  def set_wallpaper_options(self, item, data):
    if item.get_active():
      self.SETTINGS.set_wallpaper_options(data)

  # Build favorites submenu
  def build_favorites_menu(self):
    favorites_menu = gtk.Menu()

    add_favorite_menu = gtk.MenuItem()
    add_favorite_menu.set_label("Add Current")
    add_favorite_menu.connect("activate", self.APP.add_current_to_favorites)
    favorites_menu.append(add_favorite_menu)

    edit_favorites_menu = gtk.MenuItem()
    edit_favorites_menu.set_label("Edit Favorites")
    edit_favorites_menu.connect("activate", self.APP.show_favorites)
    favorites_menu.append(edit_favorites_menu)

    favorites_menu.append(gtk.SeparatorMenuItem())

    favorites = self.APP.FAVORITES_MANAGER.get_favorites()
    #for folder in favorites:
    for folder in []:
      folder_menu_item = gtk.MenuItem()
      folder_menu_item.set_label(folder)
      favorites_menu.append(folder_menu_item)
      file_menu = gtk.Menu()
      file_menu.append(self.create_favorite_menu_header(folder))
      file_menu.append(gtk.SeparatorMenuItem())
      for filename in favorites[folder]:
        file_menu.append(self.create_file_menu_item(folder, filename))
      folder_menu_item.set_submenu(file_menu)

    return favorites_menu

  # Create favorite menu header
  def create_favorite_menu_header(self, folder):
    favorite_menu_header = gtk.CheckMenuItem()
    favorite_menu_header.set_label("Use This List")
    self.FAVORITES_TOGGLES += [favorite_menu_header]
    handler = favorite_menu_header.connect(
      "toggled", self.call_set_favorite,
      {
        "folder": folder,
        "file": None
      }
    )
    favorite_menu_header.handler_block(handler)
    favorite_menu_header.set_active(
      self.SETTINGS.get_current_favorite_list() == folder
    )
    favorite_menu_header.handler_unblock(handler)
    return favorite_menu_header

  # Toggle the menu and call favorite_set appropriately
  def call_set_favorite(self, item = None, data = None):
    for menu in self.FAVORITES_TOGGLES:
      if menu != item:
        menu.handler_block_by_func(self.call_set_favorite)
        menu.set_active(False)
        menu.handler_unblock_by_func(self.call_set_favorite)
    self.APP.favorite_set(item, data, item.get_active())

  # Create a file menu item
  def create_file_menu_item(self, folder, filename):
    file_menu_item = gtk.MenuItem()
    file_menu_item.set_label(filename)
    file_menu_item.connect(
      "activate", self.APP.favorite_set, 
      {
        "folder": folder,
        "file": filename
      }
    )
    return file_menu_item

  # Append favorite menu item this gets called from favoritesmanager
  def append_favorite(self, folder, filename):
    found = False
    for menu_item in self.FAVORITES_MENU.get_submenu().get_children():
      if menu_item.get_label() == folder:
        menu_item.get_submenu().append(
          self.create_file_menu_item(folder, filename)
        )
        found = True
    if not found:
      folder_menu_item = gtk.MenuItem()
      folder_menu_item.set_label(folder)
      folder_menu_item.show()
      self.FAVORITES_MENU.get_submenu().append(folder_menu_item)
      folder_menu = gtk.Menu()
      folder_menu.append(
        self.create_file_menu_item(folder, filename)
      )
      folder_menu_item.set_submenu(folder_menu)
    self.FAVORITES_MENU.show_all()

  # Update favorites menu item
  def update_favorites(self):
    new_favorites = self.build_favorites_menu()
    new_favorites.show_all()
    self.FAVORITES_MENU.set_submenu(new_favorites)

  # Handle toggling the slidedhow menu, to be called from the CLI
  def toggle(self, active):
    self.SLIDESHOW.set_active(active)
    self.SLIDESHOW.toggled()
