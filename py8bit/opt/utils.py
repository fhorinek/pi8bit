#!/usr/bin/env python

import gtk

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
    
    if path is not None:
        dialog.set_current_folder(path)
    
    response = dialog.run()
    ret = False

    if response == gtk.RESPONSE_OK:
        ret = dialog.get_filename()
        
    dialog.destroy()
    
    while gtk.events_pending(): #   this forces the refresh of the screen
        gtk.main_iteration()    
    
    return ret