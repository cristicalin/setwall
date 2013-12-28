#!/usr/bin/python

# These need to be consistent with the gschema.xml file
APP_NAME = "wallpaper_changer"
APP_PATH = "/com/kman"
APP_ICON = "preferences-desktop-wallpaper"
BASE_ID = "com.kman"
WALLPAPER_PATH = "path"
WALLPAPER_INTERVAL = "interval"
WALLPAPER_SCHEDULE = "schedule"

# Other constants
TEXT_CONTINUE = "Continue"
TEXT_PAUSE = "Pause"

# These are gnome specific parameters
WALLPAPER_SETTING = "org.gnome.desktop.background"
PICTURE_URI = "picture-uri"
PICTURE_OPTIONS = "picture-options"

# Glade form file
GLADE_FILE = "setwall.glade"

# Logging formatter
LOG_FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'

