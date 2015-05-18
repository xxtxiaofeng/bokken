#       treeviews.py
# -*- coding: utf-8 -*-
#
#       Copyright 2011 Hugo Teso <hugo.teso@gmail.com>
#       Copyright 2014 David Martínez Moreno <ender@debian.org>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import gtk
from lib.common import datafile_path

class TreeViews(gtk.TreeView):
    '''Main TextView elements'''

    def __init__(self, core, textviews):
        self.store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)
        super(TreeViews,self).__init__(self.store)

        self.uicore = core
        self.textviews = textviews

        self.set_rules_hint(True)
        self.set_has_tooltip(True)

        # Connect right click popup search menu
        self.popup_handler = self.connect('button-press-event', self.popup_menu)
        self.popup_handler = self.connect('row-activated', self.popup_menu)

    def create_functions_columns(self):

        rendererText = gtk.CellRendererText()
        if self.uicore.backend == 'radare':
            rendererText.tooltip_handle = self.connect('motion-notify-event', self.fcn_tooltip)
        rendererPix = gtk.CellRendererPixbuf()
        self.fcn_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('function.png'))
        self.bb_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('block.png'))
        column = gtk.TreeViewColumn("Function")
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(1)
        self.store.set_sort_column_id(1,gtk.SORT_ASCENDING)
        self.append_column(column)
        self.set_model(self.store)

    def create_relocs_columns(self):

        self.data_sec_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('data-sec.png'))
        rendererPix = gtk.CellRendererPixbuf()
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name")
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        column.set_sort_column_id(0)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Virtual Address", rendererText, text=2)
        self.store.set_sort_column_id(2,gtk.SORT_ASCENDING)
        column.set_sort_column_id(2)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Type", rendererText, text=3)
        column.set_sort_column_id(3)
        self.append_column(column)

    def create_exports_columns(self):

        self.exp_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('export.png'))
        rendererPix = gtk.CellRendererPixbuf()
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Offset")
        column.set_spacing(5)
        column.pack_start(rendererPix, False)
        column.pack_start(rendererText, True)
        column.set_attributes(rendererText, text=1)
        column.set_attributes(rendererPix, pixbuf=0)
        self.store.set_sort_column_id(1,gtk.SORT_ASCENDING)
        column.set_sort_column_id(1)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", rendererText, text=2)
        column.set_sort_column_id(2)
        self.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Ordinal", rendererText, text=3)
        column.set_sort_column_id(3)
        self.append_column(column)
        self.set_model(self.store)

    def remove_columns(self):
        columns = self.get_columns()
        for column in columns:
            self.remove_column(column)

    def create_pdf_tree(self, pdfinfo):
        # Create the column
        pdfs = gtk.TreeViewColumn()
        pdfs.set_title("PDF Header")

        cell = gtk.CellRendererText()
        pdfs.pack_start(cell, True)
        pdfs.add_attribute(cell, "text", 0)

        cell = gtk.CellRendererText()
        pdfs.pack_start(cell, True)
        pdfs.add_attribute(cell, "text", 1)

        self.treestore = gtk.TreeStore(str, str)

        # Iterate PDF info and add to the tree
        header = ' '.join(pdfinfo[0][0:])
        it = self.treestore.append(None, [header, ''])
        for element in pdfinfo[1:-1]:
            col0 = element[0].strip("'")
            col1 = ' '.join(element[1:]).strip(' ')
            self.treestore.append( it, [col0, col1] )

        # Add column to tree
        self.append_column(pdfs)
        self.set_model(self.treestore)
        self.expand_all()

    def create_cookies_tree(self, url_cookies):
        # Create the column
        cookies = gtk.TreeViewColumn()
        cookies.set_title("Cookies")

        self.cell = gtk.CellRendererText()
        cookies.pack_start(self.cell, True)
        cookies.add_attribute(self.cell, "text", 0)
        cookies.set_attributes(self.cell, markup=0)

        cell = gtk.CellRendererText()
        cookies.pack_start(cell, True)
        cookies.add_attribute(cell, "text", 1)
        cookies.add_attribute(cell, "markup", 1)
        cell.set_property("markup", 1)

        self.treestore = gtk.TreeStore(str, str)

        # Iterate headers and add to the tree
        for cook in url_cookies:
            it = self.treestore.append(None, [cook[0], ''])
            for element in cook[1:]:
                if isinstance(element, str):
                    if ':' in element:
                        tmp = element.split(':')
                        for x in tmp:
                            x = x.split('=')
                            self.treestore.append(it, [x[0], x[1]])
                else:
                    for x in element.keys():
                        if 'httponly' in x.lower():
                            self.treestore.append(it, ["<span foreground=\"blue\"><b>%s</b></span>" % x, element[x]])
                        else:
                            self.treestore.append(it, [x, element[x]])

        # Add column to tree
        self.append_column(cookies)
        self.set_model(self.treestore)
        self.expand_all()

    def create_url_headers(self, url_headers):
        # Create the column
        headers = gtk.TreeViewColumn()
        headers.set_title("Headers")

        cell = gtk.CellRendererText()
        headers.pack_start(cell, True)
        headers.add_attribute(cell, "text", 0)

        cell = gtk.CellRendererText()
        headers.pack_start(cell, True)
        headers.add_attribute(cell, "text", 1)

        self.treestore = gtk.TreeStore(str, str)

        # Iterate headers and add to the tree
        it = self.treestore.append(None, ['URL Headers', ''])
        for element in url_headers:
            self.treestore.append(it, [element, url_headers[element]])

        # Add column to tree
        self.append_column(headers)
        self.set_model(self.treestore)
        self.expand_all()

    def create_url_tree(self, links):
        # Create the column
        imports = gtk.TreeViewColumn()
        imports.set_title("URL")

        cell = gtk.CellRendererText()
        rendererPix = gtk.CellRendererPixbuf()
        imports.pack_start(rendererPix, False)
        imports.pack_start(cell, True)
        imports.set_attributes(cell, text=1)
        imports.set_attributes(rendererPix, pixbuf=0)
        #imports.add_attribute(cell, "text", 0)

        self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str)

        self.remote_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('function.png'))
        self.local_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('block.png'))
        self.exp_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('export.png'))
        self.data_sec_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('data-sec.png'))

        # Iterate links and add to the tree
        it = self.treestore.append(None, [self.remote_pix, 'Remote links'])
        for element in links['remotes']:
            self.treestore.append(it, [self.remote_pix, element + '\t' + ''])
        it = self.treestore.append(None, [self.local_pix, 'Local resources'])
        for element in links['locals']:
            self.treestore.append(it, [self.local_pix, element + '\t' + ''])

        # Add column to tree
        self.append_column(imports)
        self.set_model(self.treestore)
        self.expand_all()

    def create_tree(self, imps):
        # Create the column
        imports = gtk.TreeViewColumn()
        imports.set_title("Imports")
        imports.set_spacing(5)

        self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str)

        self.imp_pix = gtk.gdk.pixbuf_new_from_file(datafile_path('import.png'))
        rendererPix = gtk.CellRendererPixbuf()
        rendererText = gtk.CellRendererText()
        imports.pack_start(rendererPix, False)
        imports.pack_start(rendererText, True)
        imports.set_attributes(rendererText, text=1)
        imports.set_attributes(rendererPix, pixbuf=0)

        # Iterate imports and add to the tree
        for element in imps.keys():
            it = self.treestore.append(None, [self.fcn_pix, element])
            for imp in imps[element]:
                self.treestore.append(it, [self.imp_pix, imp[0] + '\t' + imp[1]])

        # Add column to tree
        self.append_column(imports)
        self.set_model(self.treestore)
        self.expand_all()

    def search_and_graph(self, widget, link_name):
        self.textviews.search(widget, link_name)
        if self.dograph:
            self.textviews.update_graph(widget, link_name)

    def fcn_tooltip(self, widget, event):
        x = int(event.x)
        y = int(event.y)
        tup = widget.get_path_at_pos(x, y)
        if "Function" == tup[1].get_title():
            model = widget.get_model()
            tree_iter = model.get_iter(tup[0])
            fcn = model.get_value(tree_iter, 1)
            value = self.uicore.send_cmd_str('pdi 15 @ ' + fcn)
            widget.set_tooltip_markup("<span font_family=\"monospace\">" + value.rstrip() + "</span>")
        else:
            widget.set_tooltip_markup("")

    def popup_menu(self, tv, event, row=None):
        '''Controls the behavior of the treeviews on the left:

        Left-click or Enter/Space: Goes to the corresponding graph/address/etc.
        Right-click: Shows a menu.

        @param tv: The treeview.
        @parameter event: The GTK event (gtk.gdk.Event) in case this is a mouse
            click.  Otherwise it's the activated row index in format (n,).
        @parameter row: A gtk.TreeViewColumn object in case it's a keypress,
            otherwise None.

        The function works by abstracting the event type and then defining
        primary_action (True if left-click or Enter on a row, False if
        double_click).
        '''

        self.dograph = False

        # Let's get the row clicked whether it was by mouse or keyboard.
        if row:
            # Keyboard.
            path = event
            primary_action = True
        else:
            # Mouse.
            # I do this to return fast (and to avoid leaking memory in 'e io.va' for now).
            if (event.button != 1) and (event.button !=3):
                return False
            elif event.button == 1:
                # Left-click.
                primary_action = True
            else:
                primary_action = False

            coordinates = tv.get_path_at_pos(int(event.x), int(event.y))
            # coordinates is None if the click is outside the rows but inside
            # the widget.
            if not coordinates:
                return False
            (path, column, x, y) = coordinates

        # FIXME: We should do this on the uicore, possibly in every operation.
        if self.uicore.backend == 'radare':
            if self.uicore.use_va:
                self.uicore.core.cmd0('e io.va=0')
            else:
                self.uicore.core.cmd0('e io.va=1')

        # Main loop, deciding whether to take an action or display a pop-up.
        if primary_action:
            # It's a left click or Enter on a row.
            # Is it over a plugin name?
            # Get the information about the row.
            if len(path) == 1:
                link_name = self.store[path][1]
                # Special for exports
                if '0x' in link_name:
                    link_name = self.store[path][2]
            else:
                link_name = self.treestore[path][1]

            # Detect if search string is from URL or PE/ELF
            link_name = link_name.split("\t")
            # Elf/PE (function)
            if len( link_name ) == 1:
                if self.uicore.backend == 'pyew':
                    if '0x' in link_name[0]:
                        rva = int(link_name[0], 16) - self.uicore.core.pe.OPTIONAL_HEADER.ImageBase
                        link_name = hex( self.uicore.core.pe.get_offset_from_rva(rva) )
                    else:
                        link_name = 'FUNCTION ' + link_name[0]
                elif self.uicore.backend == 'radare':
                    if '0x' in link_name[0]:
                        link_name = link_name[0]
                    elif 'reloc.' in link_name[0]:
                            link_name = link_name[0]
                    else:
                        # Just get graph for functions
                        if not 'loc.' in link_name[0] and link_name[0][0] != '.':
                            self.dograph = True
                        # Adjust section name to search inside r2 flags
                        link_name = "0x%08x" % self.uicore.core.num.get(link_name[0])
            # Elf/PE (import/export)
            elif len( link_name ) == 2 and link_name[1] != '':
                link_name =  "0x%08x" % int(link_name[0], 16)

            # URL
            else:
                link_name = link_name[0]

            if self.uicore.backend == 'radare':
                self.search_and_graph(self, link_name)
            else:
                self.textviews.search(self, link_name)
            self.dograph = False

        else:
            # It's a right click!
            _time = event.time
            # Is it over a plugin name?
            # Get the information about the click.
            if len(path) == 1:
                link_name = self.store[path][1]
            else:
                link_name = self.treestore[path][1]

            # Detect if search string is from URL or PE/ELF
            link_name = link_name.split("\t")
            # Elf/PE (function)
            if len( link_name ) == 1:
                if self.uicore.backend == 'pyew':
                    if '0x' in link_name[0]:
                        rva = int(link_name[0], 16) - self.uicore.core.pe.OPTIONAL_HEADER.ImageBase
                        link_name = hex( self.uicore.core.pe.get_offset_from_rva(rva) )
                    else:
                        link_name = 'FUNCTION ' + link_name[0]
                elif self.uicore.backend == 'radare':
                    if '0x' in link_name[0]:
                        link_name = link_name[0]
                    elif 'reloc.' in link_name[0]:
                        link_name = link_name[0]
                    else:
                        # Just get graph for functions
                        if not 'loc.' in link_name[0] and link_name[0][0] != '.':
                            self.dograph = True
                        # Adjust section name to search inside r2 flags
                        link_name = "0x%08x" % self.uicore.core.num.get(link_name[0])
            # Elf/PE (import/export)
            elif len( link_name ) == 2 and link_name[1] != '':
                link_name =  "0x%08x" % int(link_name[0], 16)

            # URL
            else:
                link_name = link_name[0]

            # Ok, now I show the popup menu !
            # Create the popup menu
            gm = gtk.Menu()

            # And the items
            e = gtk.MenuItem("Go to")
            if 'radare' in self.uicore.backend:
                e.connect('activate', self.search_and_graph, link_name)
            else:
                e.connect('activate', self.textviews.search, link_name)
            gm.append( e )
            if 'radare' in self.uicore.backend and self.dograph:
                e = gtk.MenuItem("Show graph")
                e.connect('activate', self.textviews.update_graph, link_name)
                gm.append( e )
            gm.show_all()

            gm.popup( None, None, None, event.button, _time)
