#!/bin/bash

cp com.kman.wallpaper-changer.gschema.xml /usr/share/glib-2.0/schemas/
chown root:root /usr/share/glib-2.0/schemas/com.kman.wallpaper-changer.gschema.xml
glib-compile-schemas /usr/share/glib-2.0/schemas/
