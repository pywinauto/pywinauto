#!/usr/bin/python3

from gi import require_version
require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Gdk


software_list = [("Firefox", 2002,  "C++"),
                 ("Eclipse", 2004, "Java" ),
                 ("Pitivi", 2004, "Python"),
                 ("Netbeans", 1996, "Java"),
                 ("Chrome", 2008, "C++"),
                 ("Filezilla", 2001, "C++"),
                 ("Bazaar", 2005, "Python"),
                 ("Git", 2005, "C"),
                 ("Linux Kernel", 1991, "C"),
                 ("GCC", 1987, "C"),
                 ("Frostwire", 2004, "Java")]


def _add_image_widget():
    width = 48
    height = 24
    color = Gdk.color_parse("orange")
    pixel = 0
    if color is not None:
        pixel = ((color.red >> 8) << 24
                | (color.green >> 8) << 16
                | (color.blue >> 8) << 8)

    pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, width, height)
    pixbuf.fill(pixel)
    img = Gtk.Image.new_from_pixbuf(pixbuf)
    img.set_tooltip_text("orange image")
    return img

class TestApplicationMainWindow(Gtk.Window):

    def _add_combobox(self):
        country_store = Gtk.ListStore(str)

        countries = ["Austria", "Brazil", "Belgium", "France", "Germany",
                     "Switzerland", "United Kingdom", "United States of America",
                     "Uruguay"]

        # TODO pgi segfault because https://github.com/pygobject/pgi/issues/27 .
        # TODO PyGObject uses instead pgi solve the problem but PyGObject works incorrectly on python2 + Travis venv
        for country in countries:
            country_store.append([country])

        country_combo = Gtk.ComboBox.new_with_model(country_store)
        country_combo.connect("changed", self.on_country_combo_changed)
        renderer_text = Gtk.CellRendererText()
        country_combo.pack_start(renderer_text, True)
        country_combo.add_attribute(renderer_text, "text", 0)
        country_combo.set_active(0)
        return country_combo

    def language_filter_func(self, model, index, data):
        """Test if the language in the row is the one in the filter"""
        if self.current_filter_language is None or self.current_filter_language == "None":
            return True
        else:
            return model[index][2] == self.current_filter_language

    def _add_listview(self):
        # Creating the ListStore model
        software_liststore = Gtk.ListStore(str, int, str)
        for software_ref in software_list:
            software_liststore.append(list(software_ref))
        self.current_filter_language = None

        # Creating the filter, feeding it with the liststore model
        language_filter = software_liststore.filter_new()
        # setting the filter function, note that we're not using the
        language_filter.set_visible_func(self.language_filter_func)

        # creating the treeview, making it use the filter as a model, and adding the columns
        treeview = Gtk.TreeView.new_with_model(language_filter)
        for i, column_title in enumerate(["Software", "Release Year", "Programming Language"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            treeview.append_column(column)
        return treeview

    def _create_textview(self):
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("This is some text inside of a Gtk.TextView. \n"
            + "Select text and click one of the buttons 'bold', 'italic', \n"
            + "or 'underline' to modify the text accordingly.")
        scrolledwindow.add(self.textview)
        return scrolledwindow

    def __init__(self):
        Gtk.Window.__init__(self, title="MainWindow")
        self.set_default_size(600, 200)
        self.set_border_width(0)

        grid = Gtk.Grid()
        self.add(grid)

        self.button1 = Gtk.Button(label="Click")
        self.button1.connect("clicked", self.on_click_me_clicked)

        self.button2 = Gtk.Button(stock=Gtk.STOCK_OPEN)
        self.button2.connect("clicked", self.on_open_clicked)

        self.button3 = Gtk.Button(label="C_l_o_s_e", use_underline=True)
        self.button3.connect("clicked", self.on_close_clicked)

        self.button4 = Gtk.CheckButton(label="Button 1")
        self.button4.connect("toggled", self.on_button_toggled, "1")

        self.button5 = Gtk.CheckButton(label="Editable", use_underline=True)
        self.button5.set_active(True)
        self.button5.connect("toggled", self.on_text_editable_button_toggled, "2")

        self.label = Gtk.Label(label="Status")
        self.combo = self._add_combobox()
        self.treeview = self._add_listview()
        self.image = _add_image_widget()

        self.scroll_view = self._create_textview()
        grid.attach(self.treeview, 0, 5, 3, 1)
        grid.attach(self.combo, 0, 4, 3, 1)
        grid.attach(self.scroll_view, 0, 3, 3, 1)
        grid.attach(self.label, 0, 2, 3, 1)
        grid.attach(self.button5, 1, 1, 1, 1)
        grid.attach(self.button4, 0, 1, 1, 1)
        grid.attach(self.button3, 2, 0, 1, 1)
        grid.attach(self.button2, 1, 0, 1, 1)
        grid.attach(self.button1, 0, 0, 1, 1)
        grid.attach(self.image, 2, 1, 1, 1)

    def on_click_me_clicked(self, button):
        self._log("\"Click\" clicked")
        button.set_label("{} clicked".format(button.get_label()))

    def on_open_clicked(self, button):
        self._log("\"Open\" clicked")

    def on_close_clicked(self, button):
        self._log("Closing application")
        Gtk.main_quit()

    def on_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        self._log("Button {} turned {}".format(name, state))

    def on_text_editable_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
            self.textview.set_editable(True)
        else:
            self.textview.set_editable(False)
            state = "off"
        self._log("Button {} turned {}".format(name, state))

    def on_country_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][0]
            self._log("Selected: country={}".format(country))

    def _log(self, log):
        print(log)
        self.label.set_label(log)


win = TestApplicationMainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
