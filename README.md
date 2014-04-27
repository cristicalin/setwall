Setwall is a wallpaper manager designed to work with appindicator (designed 
by Ubuntu) but integrates into both Unity Desktop and Gnome 3. To use the 
application with the Gnome 3 desktop, you will need to install support for 
old application icons. One such example is this extension: 
https://extensions.gnome.org/extension/495/topicons/

Pre-requisite python modules:

Ubuntu 13.10+
* apsheduler (python-apscheduler)
* urllib2 (part of main python)
* simplejson (python-simplejson)
* pyinotify (python-pyinotify)
* Keybinder (gir1.2-keybinder-3.0)
* Gtk3 bindings (gir1.2-gtk-3.0)

Fedora
* AppIndicator3 (libappindicator-gtk3)
* apsheduler (pip install apscheduler)
* urllib2 (part of main python)
* simplejson (part of main python)
* pyinotify (python-inotify)
* Keybinder (keybinder3-devel)
* Gtk3 bindings (gtk3-devel)

Installing the schema file, this is necessary for the gsettings to work:

$ sudo cp com.kman.wallpaper-changer.gschema.xml \
  /usr/share/glib-2.0/schemas/
$ sudo chown root:root \
  /usr/share/glib-2.0/schemas/com.kman.wallpaper-changer.gschema.xml
$ sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

You can check by using gsettings command:

$ gsettings list-keys com.kman.wallpaper-changer

NOTE: there seems to be a X11 resource leak in Nautilus,
please make sure to disable the background-fade feature
as that seems to slow down the leak or even prevent it

$ gsettings set org.gnome.nautilus.desktop background-fade false

In order to identify if the leak is happening you can run this:

$ xrestop -b -m 1 | grep -c unknown.*PID

Normally it should return a small number about the number (<20).
xrestop is part of the xrestop package.

On Ubuntu 12.04 the keybinder-3 package needs to be built by hand.
Instructions on building keybinder-3:
* download the sources (.dsc, .orig.tar.gz, .debian.tar.gz) from
  http://packages.ubuntu.com/source/quantal/keybinder-3.0
* apt-get install pbuilder
* sudo pbuilder --init
* sudo pbuilder --update
* sudo pbuilder --build *.dsc
* dpkg -i /var/cache/pbuilder/result/*.deb
* apt-get -f install (to fix dependencies)
