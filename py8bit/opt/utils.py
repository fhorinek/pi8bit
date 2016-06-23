#!/usr/bin/env python

import gtk
import os

def process_gui_events():
    while gtk.events_pending(): #   this forces the refresh of the screen
        gtk.main_iteration()         

def gui_alert(title, text):
    dialog = gtk.Dialog(title, parent=None, flags=gtk.DIALOG_MODAL, 
        buttons= (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(gtk.RESPONSE_OK)
    
    label = gtk.Label(text)
    dialog.vbox.pack_start(label, True, True, 0)
    label.show()
    
    dialog.run()
    dialog.destroy()
    
    process_gui_events()


def gui_textedit(title, text):
    dialog = gtk.Dialog(title, parent=None, flags=gtk.DIALOG_MODAL, 
        buttons= (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                    gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    dialog.set_default_response(gtk.RESPONSE_REJECT)
    
    label = gtk.Label(title)
    dialog.vbox.pack_start(label, True, True, 0)
    label.show()
    
    edit = gtk.Entry()
    edit.set_text(text)
    dialog.vbox.pack_start(edit, True, True, 0)
    edit.show()    
    
    response = dialog.run()
    if response == gtk.RESPONSE_ACCEPT:
        text = edit.get_text()
    
    dialog.destroy()
    
    process_gui_events()    
    
    return text

def file_opendialog(path = None):
    dialog = gtk.FileChooserDialog("Chose file",
                                   None,
                                   gtk.FILE_CHOOSER_ACTION_OPEN,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)
    
    filt = gtk.FileFilter()
    filt.set_name("All files")
    filt.add_pattern("*")
    dialog.add_filter(filt)
    
    if path is None:
        path = os.getcwd()
        
    dialog.set_current_folder(path)
    
    
    response = dialog.run()
    ret = False

    if response == gtk.RESPONSE_OK:
        ret = dialog.get_filename()
        ret = os.path.relpath(ret, os.getcwd())
        
    dialog.destroy()
    
    process_gui_events() 
    
    return ret