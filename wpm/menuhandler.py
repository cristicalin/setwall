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

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

import globals

# Manage setwall application menu
class menuhandler():

  def __init__(self, app):
    self.APP = app
    self.SETTINGS = app.SETTINGS
    self.INDICATOR = appindicator.Indicator.new(
      globals.APP_SETTINGS, globals.APP_ICON,
      appindicator.IndicatorCategory.APPLICATION_STATUS
    )
    self.INDICATOR.set_status(appindicator.IndicatorStatus.ACTIVE)
    self.INDICATOR.set_menu(self.get_app_menu())

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
        "activate", 
        lambda item, data: self.SETTINGS.set_wallpaper_options(data),
        option
      )
      options_group = menu_option.get_group()
      if option == tmp_wp_options:
        menu_option.set_active(True)
      options_menu.append(menu_option)
    options_menu_item.set_submenu(options_menu)

    slideshow_menu = gtk.CheckMenuItem("Slideshow")
    slideshow_menu.connect("toggled", self.APP.toggle)
    slideshow_menu.set_active(self.SETTINGS.get_wallpaper_schedule())
    menu.append(slideshow_menu)
    self.SLIDESHOW = slideshow_menu

    menu.append(gtk.SeparatorMenuItem())

    settings_menu = gtk.MenuItem("Settings")
    settings_menu.connect("activate", self.APP.show_settings)
    menu.append(settings_menu)

    quit_menu = gtk.MenuItem("Quit")
    quit_menu.connect("activate", self.APP.quit_app)
    menu.append(quit_menu)

    menu.show_all()
    return menu

  # Handle toggling the slidedhow menu
  def toggle(self, active):
    self.SLIDESHOW.set_active(active)
    self.SLIDESHOW.toggled()
