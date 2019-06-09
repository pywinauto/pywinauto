import sys

if sys.version_info > (3, 0):
    import pgi as gi
    gi.install_as_gi()

from gi import require_version
require_version("Gtk", "3.0")

from gi.repository import Gtk


class TestApplicationMainWindow(Gtk.Window):

    def _add_combobox(self):
        country_store = Gtk.ListStore(int)

        countries = [1, 1, 1]

        # TODO pgi segfault because https://github.com/pygobject/pgi/issues/27 .
        # TODO PyGObject uses instead pgi solve the problem but PyGObject works incorrectly on python2 + Travis venv
        for country in countries:
            country_store.append([country])

        country_combo = Gtk.ComboBox.new_with_model(country_store)
        country_combo.connect("changed", self.on_country_combo_changed)
        return country_combo

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

        self.button1 = Gtk.Button("Click")
        self.button1.connect("clicked", self.on_click_me_clicked)

        self.button2 = Gtk.Button(stock=Gtk.STOCK_OPEN)
        self.button2.connect("clicked", self.on_open_clicked)

        self.button3 = Gtk.Button("C_l_o_s_e", use_underline=True)
        self.button3.connect("clicked", self.on_close_clicked)

        self.button4 = Gtk.CheckButton("Button 1")
        self.button4.connect("toggled", self.on_button_toggled, "1")

        self.button5 = Gtk.CheckButton("Editable", use_underline=True)
        self.button5.set_active(True)
        self.button5.connect("toggled", self.on_text_editable_button_toggled, "2")

        self.label = Gtk.Label("Status")
        # self.combo = self._add_combobox()

        self.scroll_view = self._create_textview()
        grid.attach(self.scroll_view, 0, 3, 3, 1)
        grid.attach(self.label, 0, 2, 3, 1)
        grid.attach(self.button5, 1, 1, 1, 1)
        grid.attach(self.button4, 0, 1, 1, 1)
        grid.attach(self.button3, 2, 0, 1, 1)
        grid.attach(self.button2, 1, 0, 1, 1)
        grid.attach(self.button1, 0, 0, 1, 1)

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
print(win.get_size().width)
print(win.get_size().height)
Gtk.main()
