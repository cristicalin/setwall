#!/usr/bin/env python
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

# These need to be consistent with the gschema.xml file
APP_NAME = "wallpaper_changer"
APP_SETTINGS = APP_NAME.replace("_", "-")
APP_FRIENDLY_NAME = " ".join(map(lambda s: s.capitalize(), APP_NAME.split("_")))
APP_PATH = "/com/kman"
APP_ICON = "preferences-desktop-wallpaper"
BASE_ID = "com.kman"

WALLPAPER_PATH = "path"
WALLPAPER_RECURSIVE = "recursive"
WALLPAPER_INTERVAL = "interval"
WALLPAPER_SCHEDULE = "schedule"
WALLPAPER_SAVED_LIST = "saved-list"
WALLPAPER_SAVE = "save"
WALLPAPER_FAVORITES = "favorites"
WALLPAPER_RECONCILE = "reconcile"
WALLPAPER_VERIFY_PRESENCE = "verify-presence"
WALLPAPER_VERIFY_IMAGE = "verify-image"
WALLPAPER_CURRENT_FAVORITE = "current-favorite-list"

# These are gnome specific parameters
WALLPAPER_SETTING = "org.gnome.desktop.background"
PICTURE_URI = "picture-uri"
PICTURE_OPTIONS = "picture-options"

# Global keys
KEY_NEXT = "next-key"
KEY_PREVIOUS = "previous-key"
KEY_FAVORITE = "favorite-key"

# ScreenSaver parameters
SCREEN_SAVER_NAME = "org.gnome.ScreenSaver"
SCREEN_SAVER_PATH = "/%s" % SCREEN_SAVER_NAME.replace(".", "/")
SCREEN_SAVER_SIGNAL = "ActiveChanged"

# Glade form file
GLADE_SETTINGS_FILE = "settings.glade"
GLADE_FAVORITES_FILE = "favorites.glade"

# Logging formatter
LOG_FORMAT = '%(asctime)-15s %(message)s'

