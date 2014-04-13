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

# This class is used only to provide callbacks for the favorites dialog
class favoriteshandler:

  def __init__(self, favorites):
    self.FAVORITES = favorites
    self.drag = False
    self.drag_x = 0
    self.drag_y = 0
    self.ARROW = gdk.Cursor(gdk.CursorType.ARROW)
    self.CROSS = gdk.Cursor(gdk.CursorType.DIAMOND_CROSS)

  def get_selected(self):
    selection = self.FAVORITES.TREE_VIEW.get_selection()
    return selection.get_selected()

  def get_selected_data(self):
    (model, tree_iter) = self.get_selected()
    if tree_iter is not None:
      filename = model[tree_iter][0]
      parent_iter = model.iter_parent(tree_iter)
      if parent_iter is not None:
        folder = model[parent_iter][0]
        return folder, filename
    return None, None

  def swap_iters(self, func):
    (model, tree_iter) = self.get_selected()
    if model is not None and tree_iter is not None:
      try:
        swap_iter = func(model, tree_iter)
        model.swap(tree_iter, swap_iter)
      except:
        None

  def onDeleteEvent(self, *args):
    # prevent window from clearing out resources on detele call
    self.FAVORITES.hide_window()
    return True

  def onSave(self, *args):
    self.FAVORITES.save_favorites()
    self.FAVORITES.hide_window()

  def onClose(self, *args):
    self.FAVORITES.hide_window()

  def onSet(self, *args):
    folder, filename = self.get_selected_data()
    if folder is not None and filename is not None:
      self.FAVORITES.APP.favorite_set(
        data = { "folder": folder, "file": filename}
      )

  def onUp(self, *args):
    self.swap_iters(lambda a, b: a.iter_previous(b))

  def onDown(self, *args):
    self.swap_iters(lambda a, b: a.iter_next(b))

  def onDelete(self, *args):
    (model, tree_iter) = self.get_selected()
    if model is not None and tree_iter is not None:
      parent_iter = model.iter_parent(tree_iter)
      model.remove(tree_iter)
      if parent_iter is not None:
        if not model.iter_has_child(parent_iter):
          model.remove(parent_iter)

  def onCursorChanged(self, *args):
    folder, filename = self.get_selected_data()
    if folder is not None and filename is not None:
      self.FAVORITES.show_preview(folder, filename)          

  def onZoomIn(self, *args):
    self.FAVORITES.display_zoomed_in_image()

  def onZoomOut(self, *args):
    self.FAVORITES.display_zoomed_out_image()

  # we get the onMouse* events from a GtkEventBox so that the coordinates
  # always refer to the same fixed points otherwise we get jerky movement
  # save current mouse position and turn the cursor into a cross
  def onMouseGrab(self, *args):
    event = args[1]
    self.drag = True
    self.drag_x = event.x
    self.drag_y = event.y
    self.FAVORITES.PREVIEW_SCROLL.get_root_window().set_cursor(self.CROSS)

  # use GtkAdjustment to move the preview picture
  def onMouseMove(self, *args):
    if self.drag:
      event = args[1]
      diff_x = self.drag_x - event.x
      diff_y = self.drag_y - event.y
      self.drag_x = event.x
      self.drag_y = event.y
      adj_x, adj_y = self.FAVORITES.get_adjustments()
      self.FAVORITES.set_adjustments(adj_x + diff_x, adj_y + diff_y)
      
  # release the drag and change the cursor back
  def onMouseRelease(self, *args):
    self.drag = False
    self.FAVORITES.PREVIEW_SCROLL.get_root_window().set_cursor(self.ARROW)

# this is for unit testing only
if __name__ == "__main__":
  fm = favoriteshandler()