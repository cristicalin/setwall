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

# this code library contains useful stand alone functions

# Shorten long file names
def shorten(data, length):
  info = (data[:int(length/2)-1] + '..' + 
          data[-(int(length/2)-1):]) if len(data) > length else data
  return info

# this is for unit testing only
if __name__ == "__main__":
  
  print shorten("very long string more than 16 chars in length", 16)
