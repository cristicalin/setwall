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
import copy

from urllib2 import quote, unquote
from apscheduler.scheduler import Scheduler

from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject

# Local imports
from globals import *
from settings import *
from filelist import *
from wallpapermanager import *
from dbushandler import *
from menuhandler import *
from utils import *

# This is the main application class
class application:

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
    
    self.MENU_OBJECT = menuhandler(self)
    self.SESSION_OBJECT = dbushandler(self)
    self.FILE_LIST = filelist(self)
    self.load_settings()
    self.WALLPAPER_MANAGER = wallpapermanager(self.SETTINGS)
    self.set_index()
    self.SCHEDULER.start()

  # Greacefuly quit the application
  def quit_app(self, item = None):
    # we neet to stop both the notifier as well as the gtk main loop
    self.save_json()
    self.FILE_LIST.close()
    gtk.main_quit()

  def next_wallpaper(self, item = None):
    self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_next_file())
    self.reset_schedule()

  def previous_wallpaper(self, item = None):
    self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_previous_file())
    self.reset_schedule()

  def toggle(self, item = None):
    if item != None:
      self.SETTINGS.set_wallpaper_schedule(item.get_active())
      if self.SETTINGS.get_wallpaper_schedule():
        self.resume_schedule()
      else:
        self.suspend_schedule()
    else:
      self.MENU_OBJECT.toggle(not self.SETTINGS.get_wallpaper_schedule())

  def show_settings(self, item = None):
    self.SETTINGS.show_window()

  def file_changed(self, action, filename):
    if action == "add":
      self.WALLPAPER_MANAGER.show_notification(
        "Wallpaper Added",
        "New file: %s" % shorten(filename.split("/")[-1], 32),
        "file://%s" % quote(filename)
      )
    elif action == "remove":
      self.WALLPAPER_MANAGER.show_notification(
        "Wallpaper Removed",
        "Removed file: %s" % shorten(filename.split("/")[-1], 32),
        None
      )

  # Reset the scheduler
  def reset_schedule(self):
    self.suspend_schedule()
    self.resume_schedule()

  # Suspend the scheduler
  def suspend_schedule(self):
    for job in self.SCHEDULER.get_jobs():
      self.SCHEDULER.unschedule_job(job)

  # Resume the scheduler
  def resume_schedule(self):
    if self.SETTINGS.get_wallpaper_schedule():
      self.SCHEDULER.add_interval_job(self.next_wallpaper,
                                      seconds = self.SETTINGS.get_wallpaper_interval())

  # Load and process settings, will be also called
  # when apply is pressed in the settings dialog
  # reload = False and file_list = None -> initial call
  # reload = True and file_list != None -> call from settings
  def load_settings(self, reload = False, file_list = None):
    if not reload:
      if self.SETTINGS.get_wallpaper_save():
        self.FILE_LIST.load(self.SETTINGS.get_wallpaper_path(),
                            self.SETTINGS.get_saved_list())
      else:
        self.FILE_LIST.load(self.SETTINGS.get_wallpaper_path())
    else:
      if (self.SETTINGS.LOCAL_FILE_LIST.get_current_file() != 
          self.FILE_LIST.get_current_file()):
        self.FILE_LIST.close()
        self.FILE_LIST = copy.copy(self.SETTINGS.LOCAL_FILE_LIST)
        self.WALLPAPER_MANAGER.set_wallpaper(self.FILE_LIST.get_current_file())
      # Only save json upon a change
      # this means that we will not save indiscriminately
      # so we also have to save_json() on exit
      self.save_json()

    self.reset_schedule()

  # Set the file list index to the current wallpaper
  # this gets called multiple times so it became a function
  def set_index(self):
    self.FILE_LIST.set_index(self.WALLPAPER_MANAGER.get_wallpaper())

  # Save the current file_list json format to the settings
  # only if it actually requires saving
  def save_json(self):
    if self.SETTINGS.get_wallpaper_save() and self.FILE_LIST.get_need_save():
      self.SETTINGS.set_saved_list(self.FILE_LIST.get_json())
      self.FILE_LIST.set_need_save(False)

  def main(self):
    gtk.main()
    

# main function call creates application object and starts processing
# this is for unit testing only
if __name__ == "__main__":
  # allow other threads to execute
  import dbus
  
  dbus.glib.init_threads()
  gobject.threads_init()

  app = application()
  app.main()
  sys.exit(0)
