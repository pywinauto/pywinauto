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

        self.button1 = Gtk.Button("Click")
        self.button1.connect("clicked", self.on_click_me_clicked)
        main_objects_box.pack_start(self.button1, True, True, 0)

        self.button2 = Gtk.Button(stock=Gtk.STOCK_OPEN)
        self.button2.connect("clicked", self.on_open_clicked)
        main_objects_box.pack_start(self.button2, True, True, 0)

        self.button3 = Gtk.Button("C_l_o_s_e", use_underline=True)
        self.button3.connect("clicked", self.on_close_clicked)
        main_objects_box.pack_start(self.button3, True, True, 0)

        self.button4 = Gtk.CheckButton("Button 1")
        self.button4.connect("toggled", self.on_button_toggled, "1")
        main_objects_box.pack_start(self.button4, False, False, 0)

        self.button5 = Gtk.CheckButton("B_u_t_t_o_n 2", use_underline=True)
        self.button5.set_active(True)
        self.button5.connect("toggled", self.on_button_toggled, "2")
        main_objects_box.pack_start(self.button5, False, False, 0)

        self.label = Gtk.Label("Status")
        main_objects_box.pack_start(self.label, False, False, 0)

    def on_click_me_clicked(self, button):
        print("\"Click\" clicked")
        self.label.set_label("\"Click\" clicked")
        button.set_label("{} clicked".format(button.get_label()))

    def on_open_clicked(self, button):
        self.label.set_label("\"Open\" clicked")
        print("\"Open\" clicked")

    def on_close_clicked(self, button):
        self.label.set_label("Closing application")
        print("Closing application")
        Gtk.main_quit()

    def on_button_toggled(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        self.label.set_label("Button {} turned {}".format(name, state))
        print("Button {} turned {}".format(name, state))


win = TestApplicationMainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
print(win.get_size().width)
print(win.get_size().height)
Gtk.main()
