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

from gi.repository import Gdk as gdk

# This class is used only to provide callbacks for the settings dialog
class settingshandler:

  def __init__(self, settings):
    self.SETTINGS = settings
    self.BINDINGS_MANAGER = settings.APP.BINDINGS_MANAGER

  def onApply(self, *args):
    self.SETTINGS.save()
    self.SETTINGS.hide_window()

  def onDeleteEvent(self, *args):
    self.SETTINGS.hide_window()
    return True
    
  def onClose(self, *args):
    self.SETTINGS.hide_window()
    
  def onPathChanged(self, *args):
    self.SETTINGS.set_path(args[0].get_active_text(), True)

  def onSlideshowToggle(self, *args):
    self.SETTINGS.spInterval.set_sensitive(
      self.SETTINGS.ckSchedule.get_active()
    )

  def onPrevious(self, *args):
    filename = "file://%s" % self.SETTINGS.LOCAL_FILE_LIST.get_previous_file()
    self.SETTINGS.STATUS_BAR.push(0, filename)
    self.SETTINGS.show_preview(filename)

  def onNext(self, *args):
    filename = "file://%s" % self.SETTINGS.LOCAL_FILE_LIST.get_next_file()
    self.SETTINGS.STATUS_BAR.push(0, filename)
    self.SETTINGS.show_preview(filename)

  def onToggleKey(self, widget, user_data):
    self.SETTINGS.flip_toggles(widget)
    if widget.get_active():
      self.BINDINGS_MANAGER.suspend_bindings()
      self.disconnect()
      self.KEY_HANDLER = self.SETTINGS.WINDOW.connect(
        "key-press-event", self.onKeyPress,
        [self.setKey, widget, user_data] 
      )
    else:
      self.disconnect(True)

  def onKeyPress(self, widget, event, data):
    key = gdk.keyval_name(event.keyval)
    ctrl = event.state & gdk.ModifierType.CONTROL_MASK
    alt = event.state & gdk.ModifierType.MOD1_MASK
    shift = event.state & gdk.ModifierType.SHIFT_MASK
    modifiers = []
    if ctrl:
      modifiers.append("<Ctrl>")
    if alt:
      modifiers.append("<Alt>")
    if shift:
      modifiers.append("<Shift>")
    modifiers.append(key)
    data[0](data[1], data[2], "".join(modifiers))

  def setKey(self, widget, name, key):
    if self.BINDINGS_MANAGER.is_usable(name, key):
      widget.set_label(key)

  def onLeave(self, widget):
    widget.set_active(False)

  def disconnect(self, resume = False):
    try:
      self.SETTINGS.WINDOW.disconnect(self.KEY_HANDLER)
      self.KEY_HANDLER = None
      if resume:
        self.BINDINGS_MANAGER.resume_bindings()
    except:
      None

# this is for unit testing only
if __name__ == "__main__":
  sh = settingshandler()