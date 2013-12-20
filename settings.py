#!/usr/bin/python

import sys
import os

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk

import globals

class settings:

  class handler:

    def __init__(self, settings):
      self.settings = settings

    def onApplyClicked(self, *args):
      self.settings.hide_window()

    def onClose(self, *args):
      self.settings.hide_window()

  def __init__(self):
    self.builder = gtk.Builder()
    try:
      self.builder.add_from_file("%s/%s" % (os.path.dirname(sys.argv[0]), globals.GLADE_FILE))
    except:
      self.builder.add_from_file(globals.GLADE_FILE)
    self.builder.connect_signals(self.handler(self))

    self.window = self.builder.get_object("wcMain")
    self.window.set_title(" ".join([word.capitalize() for word in globals.APP_NAME.split("_")]))
    self.window.move(gdk.Screen.width()-self.window.get_size()[0], 0)

  def show_window(self):
    self.window.show_all()

  def hide_window(self):
    self.window.hide()

  def get_window(self):
    return self.window

if __name__ == "__main__":

  s = settings()
  s.show_window()

  gtk.main()
