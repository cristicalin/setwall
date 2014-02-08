#!/usr/bin/python

import dbus
import dbus.service
import gobject
from dbus.mainloop.glib import DBusGMainLoop

class handle_dbus(dbus.service.Object):
  @dbus.service.signal(dbus_interface = 'org.gnome.ScreenSaver')
  def ActiveChanged(self, msg):
    print "called(%s)" % msg

def handler(*args, **kwargs):
  for arg in args:
    print str(arg)
  for key in kwargs:
    print kwags[key]

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
#name = dbus.service.BusName('org.gnome.ScreenSaver', bus)

service = bus.get_object('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver')
print service
bus.add_signal_receiver(handler, dbus_interface = 'org.gnome.ScreenSaver', signal_name = 'ActiveChanged')

#obj = handle_dbus(bus, '/org/gnome/ScreenSaver')

#obj.ActiveChanged(True)

loop = gobject.MainLoop()
loop.run()
