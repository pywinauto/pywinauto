import os
# from gi import require_version
# require_version("Gtk", "3.0")
import pgi
pgi.install_as_gi()
from gi.repository import Gtk, Gdk


class Handler(object):
    def on_delete_window(self, *args):
        Gtk.main_quit(*args)

    def delete_event(self, *args):
        Gtk.main_quit(*args)

    def click_button_press(self, button, event):
        print("ClickButton pressed!")
        label = builder.get_object("ClickButtonLabel")
        if event.type == Gdk.EventType.BUTTON_PRESS:
            print("Single click")
            label.set_text("Single click")
        elif event.type == Gdk.EventType._2BUTTON_PRESS:
            print("Double click")
            label.set_text("Double click")

    def toggle_button_action(self, button):
        print("Toggled: {}".format(button.get_active()))
        label = builder.get_object("ToggleButtonLabel")
        label.set_text("Toggled: {}".format(button.get_active()))

    def check_button_action(self, button):
        print("Checked: {}".format(button.get_active()))
        label = builder.get_object("CheckButtonLabel")
        label.set_text("Checked: {}".format(button.get_active()))


if __name__ == '__main__':
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ExampleUi.glade"))

    window = builder.get_object('MainWindow')
    print(window.get_size())
    builder.connect_signals(Handler())
    window.show_all()
    Gtk.main()
