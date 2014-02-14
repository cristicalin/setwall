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

import sys
import atexit
import argparse
import logging

import dbus
import dbus.service
import dbus.glib

from urllib2 import quote, unquote
from apscheduler.scheduler import Scheduler

from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject
from gi.repository import AppIndicator3 as appindicator

# Local imports
from globals import *
from settings import *
from filelist import *
from wallpapermanager import *

# This is the main application class
class application:

  # This is a handler class for the DBus messages, it allows
  # the application to receive next and previous messages
  class handledbus(dbus.service.Object):

    def __init__(self, bus, app):
      self.APP = app
      dbus.service.Object.__init__(self, bus, "%s/%s" % (APP_PATH, APP_NAME))

    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def next(self):
      self.APP.next_wallpaper()

    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                       in_signature='', out_signature='')
    def previous(self):
      self.APP.previous_wallpaper()

    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def toggle(self):
      self.APP.toggle_schedule()
    
    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def randomize(self):
      self.reorder_func(self.APP.FILE_LIST.randomize)
    
    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def sort(self):
      self.reorder_func(self.APP.FILE_LIST.sort)
    
    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def reverse(self):
      self.reorder_func(self.APP.FILE_LIST.reverse)
    
    @dbus.service.method("%s.%s" % (BASE_ID, APP_NAME),
                         in_signature='', out_signature='')
    def quit(self):
      self.APP.quit_app()
  
    def reorder_func(self, func):
      func()
      self.APP.set_index()
      self.APP.save_json()

  # application class constructor
  def __init__(self):
    self.SCHEDULER = Scheduler()
    # make sure we properly clean up after ourselves 
    atexit.register(lambda: self.SCHEDULER.shutdown(wait=True))
    # make apscheduler happy
    logging.basicConfig(format=LOG_FORMAT)

    # Parse the command line arguments
    parser = argparse.ArgumentParser(APP_FRIENDLY_NAME)
    parser.add_argument("-p", "--path", type=str,
                        help="Path in which wallpapers reside")
    parser.add_argument("-i", "--interval", type=int,
                        help="Time interval in seconds between switches")
    parser.add_argument("-s", "--schedule", type=bool,
                        help="Scheduled wallpaper changes")
    args = parser.parse_args()
    self.SETTINGS = settings(args = args, app = self)
    
    self.load_icons()
    self.INDICATOR = appindicator.Indicator.new(APP_NAME.replace("_","-"),
                                               APP_ICON,
                                               appindicator.IndicatorCategory.APPLICATION_STATUS)
    self.INDICATOR.set_status(appindicator.IndicatorStatus.ACTIVE)
    self.INDICATOR.set_menu(self.get_app_menu())
    
    self.SESSION_BUS = dbus.SessionBus()
    # we need to kill the previous instance as a first thing
    try:
      running_obj = self.SESSION_BUS.get_object("%s.%s" % (BASE_ID, APP_NAME),
                                                "%s/%s" % (APP_PATH, APP_NAME))
      running_obj.quit()
    except dbus.DBusException as e:
      None
    self.SESSION_NAME = dbus.service.BusName("%s.%s" % (BASE_ID, APP_NAME),
                                             self.SESSION_BUS)
    self.SESSION_OBJECT = self.handledbus(self.SESSION_BUS, self)
    self.SESSION_BUS.add_signal_receiver(self.screen_saver_handler,
                                         dbus_interface = SCREEN_SAVER_NAME,
                                         signal_name = SCREEN_SAVER_SIGNAL)
    
    self.FILE_LIST = filelist(self)
    self.load_settings()
    self.WALLPAPER_MANAGER = wallpapermanager(self.SETTINGS)
    self.set_index()
    self.SCHEDULER.start()

  # Greacefuly quit the application
  def quit_app(self,item = None):
    # we neet to stop both the notifier as well as the gtk main loop
    self.FILE_LIST.close()
    gtk.main_quit()

  def next_wallpaper(self, item = None):
    self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_next_file())
    self.reset_schedule()

  def previous_wallpaper(self, item = None):
    self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_previous_file())
    self.reset_schedule()

  def toggle_schedule(self, item = None, toggle = True):
    if toggle:
      self.SETTINGS.set_wallpaper_schedule(not self.SETTINGS.get_wallpaper_schedule())
    if self.SETTINGS.get_wallpaper_schedule():
      if toggle:
        self.SCHEDULER.add_interval_job(self.next_wallpaper,
                                        seconds=self.SETTINGS.get_wallpaper_interval())
      self.TOGGLE_MENU.set_image(self.stop_icon)
      self.TOGGLE_MENU.set_label(TEXT_PAUSE)
    else:
      if toggle:
        self.SCHEDULER.unschedule_func(self.next_wallpaper)
      self.TOGGLE_MENU.set_image(self.play_icon)
      self.TOGGLE_MENU.set_label(TEXT_CONTINUE)

  # suspend schedule while screen saver / lock is in place
  def screen_saver_handler(self, active):
    if self.SETTINGS.get_wallpaper_schedule():
      if active:
        self.SCHEDULER.unschedule_func(self.next_wallpaper)
      else:
        self.SCHEDULER.add_interval_job(self.next_wallpaper,
                                        seconds=self.SETTINGS.get_wallpaper_interval())

  def show_settings(self, item = None):
    self.SETTINGS.show_window()

  def file_changed(self, action, filename):
    if action == "add":
      self.WALLPAPER_MANAGER.show_notification(
        "Wallpaper Added",
        "New file: %s" % self.WALLPAPER_MANAGER.shorten(filename.split("/")[-1], 32),
	"file://%s" % quote(filename)
      )
    elif action == "remove":
      self.WALLPAPER_MANAGER.show_notification(
        "Wallpaper Removed",
        "Removed file: %s" % self.WALLPAPER_MANAGER.shorten(filename.split("/")[-1], 32),
        None
      )

  # Build the application menu which is delivered
  # via the appindicator functionality
  def get_app_menu(self):
    menu = gtk.Menu()
   
    next_menu = gtk.MenuItem()
    next_menu.set_label("Next")
    next_menu.connect("activate", self.next_wallpaper)
    menu.append(next_menu)

    prev_menu = gtk.MenuItem()
    prev_menu.set_label("Previous")
    prev_menu.connect("activate", self.previous_wallpaper)
    menu.append(prev_menu)

    options_menu_item = gtk.MenuItem()
    options_menu_item.set_label("Options");
    menu.append(options_menu_item)
    options_menu = gtk.Menu()

    options_range = self.SETTINGS.get_wallpaper_options_range()
    options_group = []
    for option in options_range[1]:
      menu_option = gtk.RadioMenuItem.new_with_label(options_group,
                                                     option.title())
      menu_option.connect("activate", 
                          lambda item, data: self.SETTINGS.set_wallpaper_options(data),
			  option)
      options_group = menu_option.get_group()
      if option == self.SETTINGS.get_wallpaper_options():
        menu_option.set_active(True)
      options_menu.append(menu_option)
    options_menu_item.set_submenu(options_menu)

    self.TOGGLE_MENU = gtk.ImageMenuItem(" ")
    self.TOGGLE_MENU.connect("activate", self.toggle_schedule)
    self.TOGGLE_MENU.set_always_show_image(True)
    menu.append(self.TOGGLE_MENU)

    menu.append(gtk.SeparatorMenuItem())

    settings_menu = gtk.MenuItem("Settings")
    settings_menu.connect("activate", self.show_settings)
    menu.append(settings_menu)

    quit_menu = gtk.MenuItem("Quit")
    quit_menu.connect("activate", self.quit_app)
    menu.append(quit_menu)

    menu.show_all()
    return menu

  # Keep icons stored in memory so we don't have to
  # reload them each time the menu is toggled
  def load_icons(self):
    self.play_icon = gtk.Image()
    self.play_icon.set_from_icon_name(gtk.STOCK_MEDIA_PLAY, gtk.IconSize.MENU)
    self.play_icon.show()
    self.stop_icon = gtk.Image()
    self.stop_icon.set_from_icon_name(gtk.STOCK_MEDIA_STOP, gtk.IconSize.MENU)
    self.stop_icon.show()

  # Reset the schedule
  def reset_schedule(self):
    for job in self.SCHEDULER.get_jobs():
      self.SCHEDULER.unschedule_job(job)
    if self.SETTINGS.get_wallpaper_schedule():
      self.SCHEDULER.add_interval_job(self.next_wallpaper,
                                      seconds = self.SETTINGS.get_wallpaper_interval())

  # Load and process settings, will be also called
  # when apply is pressed in the settings dialog
  def load_settings(self, reload = False):
    if self.SETTINGS.get_wallpaper_save():
      self.FILE_LIST.load(self.SETTINGS.get_wallpaper_path(),
                          self.SETTINGS.get_saved_list())
    else:
      self.FILE_LIST.load(self.SETTINGS.get_wallpaper_path())
    if reload:
      self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_current_file())
    self.save_json()
    self.reset_schedule()
    self.toggle_schedule(toggle=False)

  # Set the file list index to the current wallpaper
  # this gets called multiple times so it became a function
  def set_index(self):
    try:
      self.FILE_LIST.set_index(self.WALLPAPER_MANAGER.get_wallpaper())
    except Exception as e:
      None

  # Save the current file_list json format to the settings
  def save_json(self):
    if self.SETTINGS.get_wallpaper_save():
      self.SETTINGS.set_saved_list(self.FILE_LIST.get_json())

  def main(self):
    gtk.main()


# main function call creates application object and starts processing
if __name__ == "__main__":
  # allow other threads to execute
  dbus.glib.init_threads()
  gobject.threads_init()

  app = application()
  app.main()
  sys.exit(0)