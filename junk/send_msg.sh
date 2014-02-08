#!/bin/bash

dbus-send --type=signal /org/gnome/ScreenSaver org.gnome.ScreenSaver.ActiveChanged "boolean:true"
