import sys

if sys.version_info > (3, 0):
    import pgi as gi
    gi.install_as_gi()

from gi import require_version
require_version("Gtk", "3.0")

from gi.repository import Gtk


class TestApplicationMainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="MainWindow")
        self.set_default_size(600, 200)
        self.set_border_width(0)

        main_objects_box = Gtk.Box(spacing=6)
        self.add(main_objects_box)

        button = Gtk.Button("Click")
        button.connect("clicked", self.on_click_me_clicked)
        main_objects_box.pack_start(button, True, True, 0)

        button = Gtk.Button(stock=Gtk.STOCK_OPEN)
        button.connect("clicked", self.on_open_clicked)
        main_objects_box.pack_start(button, True, True, 0)

        button = Gtk.Button("C_l_o_s_e", use_underline=True)
        button.connect("clicked", self.on_close_clicked)
        main_objects_box.pack_start(button, True, True, 0)

        button = Gtk.CheckButton("Button 1")
        button.connect("toggled", self.on_button_toggled, "1")
        main_objects_box.pack_start(button, False, False, 0)

        button = Gtk.CheckButton("B_u_t_t_o_n 2", use_underline=True)
        button.set_active(True)
        button.connect("toggled", self.on_button_toggled, "2")
        main_objects_box.pack_start(button, False, False, 0)

    def on_click_me_clicked(self, button):
        print("\"Click\" clicked")

    def on_open_clicked(self, button):
        print("\"Open\" clicked")

    def on_close_clicked(self, button):
        print("Closing application")
        Gtk.main_quit()

    def on_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        print("Button", name, "turned", state)


win = TestApplicationMainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
print(win.get_size().width)
print(win.get_size().height)
Gtk.main()
