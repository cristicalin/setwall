#!/usr/bin/python

# These need to be consistent with the gschema.xml file
APP_NAME = "wallpaper_changer"
APP_FRIENDLY_NAME = " ".join(map(lambda s: s.capitalize(), APP_NAME.split("_")))
APP_PATH = "/com/kman"
APP_ICON = "preferences-desktop-wallpaper"
BASE_ID = "com.kman"
WALLPAPER_PATH = "path"
WALLPAPER_INTERVAL = "interval"
WALLPAPER_SCHEDULE = "schedule"
WALLPAPER_SAVED_LIST = "saved-list"
WALLPAPER_SAVE = "save"

# Other constants
TEXT_CONTINUE = "Continue"
TEXT_PAUSE = "Pause"

# These are gnome specific parameters
WALLPAPER_SETTING = "org.gnome.desktop.background"
PICTURE_URI = "picture-uri"
PICTURE_OPTIONS = "picture-options"

# ScreenSaver parameters
SCREEN_SAVER_NAME = "org.gnome.ScreenSaver"
SCREEN_SAVER_PATH = "/%s" % SCREEN_SAVER_NAME.replace(".", "/")
SCREEN_SAVER_SIGNAL = "ActiveChanged"

# Glade form file
GLADE_FILE = "setwall.glade"

# Settings preview parameters
PREVIEW_SCALE = 1.5
PREVIEW_WIDTH = 240
PREVIEW_HEIGHT = 160

# Logging formatter
LOG_FORMAT = '%(asctime)-15s %(user)-8s %(message)s'

