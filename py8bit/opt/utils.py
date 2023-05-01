#!/usr/bin/env python

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

def process_gui_events():
    while Gtk.events_pending(): #   this forces the refresh of the screen
        Gtk.main_iteration()

def gui_alert(title, text):
    dialog = Gtk.Dialog(title=title, transient_for=None, flags=Gtk.DialogFlags.MODAL,
        buttons=(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.OK)

    label = Gtk.Label(label=text)
    dialog.get_content_area().pack_start(label, True, True, 0)
    label.show()

    dialog.run()
    dialog.destroy()

    process_gui_events()


def gui_textedit(title, text):
    dialog = Gtk.Dialog(title=title, transient_for=None, flags=Gtk.DialogFlags.MODAL,
        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                 Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
    dialog.set_default_response(Gtk.ResponseType.REJECT)

    label = Gtk.Label(label=title)
    dialog.get_content_area().pack_start(label, True, True, 0)
    label.show()

    edit = Gtk.Entry()
    edit.set_text(text)
    dialog.get_content_area().pack_start(edit, True, True, 0)
    edit.show()

    response = dialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        text = edit.get_text()

    dialog.destroy()

    process_gui_events()

    return text

def file_opendialog(path=None):
    dialog = Gtk.FileChooserDialog("Choose file",
                                   None,
                                   Gtk.FileChooserAction.OPEN,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)

    filt = Gtk.FileFilter()
    filt.set_name("All files")
    filt.add_pattern("*")
    dialog.add_filter(filt)

    if path is None:
        path = os.getcwd()

    dialog.set_current_folder(path)

    response = dialog.run()
    ret = False

    if response == Gtk.ResponseType.OK:
        ret = dialog.get_filename()
        ret = os.path.relpath(ret, os.getcwd())

    dialog.destroy()

    process_gui_events()

    return ret
