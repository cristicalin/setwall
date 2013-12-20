#!/usr/bin/python

from gi.repository import Gtk as gtk

class handler:

  def onWindowDelete(self, *args):
    gtk.main_quit(*args)


builder = gtk.Builder()
builder.add_from_file("setwall.glade")
builder.connect_signals(handler())

window = builder.get_object("wcMain")

if __name__ == "__main__":
  window.show_all()

  gtk.main()
