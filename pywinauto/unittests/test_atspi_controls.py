import os
import sys
import time
import unittest

if sys.platform.startswith("linux"):
    sys.path.append(".")
    from pywinauto.linux.atspi_element_info import AtspiElementInfo
    from pywinauto.linux.application import Application
    from pywinauto.controls.atspiwrapper import AtspiWrapper

app_name = r"gtk_example.py"
text = "This is some text inside of a Gtk.TextView. \n" \
       "Select text and click one of the buttons 'bold', 'italic', \n" \
       "or 'underline' to modify the text accordingly."
countries = ['Austria', 'Brazil', 'Belgium', 'France', 'Germany', 'Switzerland', 'United Kingdom',
             'United States of America', 'Uruguay']


def _test_app():
    test_folder = os.path.join(os.path.dirname
                               (os.path.dirname
                                (os.path.dirname
                                 (os.path.abspath(__file__)))),
                               r"apps/Gtk_samples")
    sys.path.append(test_folder)
    return os.path.join(test_folder, app_name)


def print_tree(start_el_info, level_shifter=""):
    if level_shifter == "":
        print(start_el_info.control_type, "  ", start_el_info.name, "!")
        level_shifter += "-"

    for children in start_el_info.children():
        print(level_shifter, "  ", children.control_type, "    ", children.name, "!")
        print_tree(children, level_shifter + "-")


if sys.platform.startswith("linux"):
    class AtspiControlTests(unittest.TestCase):

        """Unit tests for the AtspiWrapper class"""

        def setUp(self):
            self.app = Application()
            self.app.start("python3.4 " + _test_app())
            time.sleep(1)
            self.app_window = self.app.gtk_example
            self.button_wrapper = self.app_window.Frame.Panel.Click.wrapper_object()
            self.button_info = self.app_window.Frame.Panel.Click.element_info
            self.text_area = self.app_window.Frame.Panel.ScrollPane.Text.wrapper_object()

        def tearDown(self):
            self.app.kill()

        def _get_state_label_text(self):
            return self.app.gtk_example.Frame.Panel.Label.window_text()

        def test_get_action(self):
            actions_count = self.button_wrapper.action.get_n_actions()
            print("Button actions count is: {}".format(actions_count))
            for i in range(actions_count):
                print("action {} is: {}. Description: {}".format(i, self.button_wrapper.action.get_action_name(i),
                                                                 self.button_wrapper.action.get_action_description(i)))

            self.assertEqual(self.button_wrapper.action.get_localized_name(0).decode('utf-8'), "Click")

        def test_do_action(self):
            status = self.button_wrapper.action.do_action(0)
            print("Action invoked, action status is: {}".format(status))
            self.assertTrue(status)

        def test_button_click(self):
            self.assertEqual(self.button_info.rich_text, "Click")
            self.button_wrapper.click()
            self.assertEqual(self.button_info.rich_text, "Click clicked")
            self.assertEqual(self._get_state_label_text(), "\"Click\" clicked")

        def test_button_toggle(self):
            toggle_button_wrapper = self.app_window.Frame.Panel.Button
            toggle_button_wrapper.click()
            self.assertEqual(self._get_state_label_text(), "Button 1 turned on")

        def test_button_toggle_state(self):
            toggle_button_wrapper = self.app_window.Frame.Panel.Button
            self.assertFalse(toggle_button_wrapper.get_toggle_state())
            toggle_button_wrapper.click()
            self.assertTrue(toggle_button_wrapper.get_toggle_state())

        def test_text_area_is_editable(self):
            editable_state_button = self.app_window.Frame.Panel.Editable
            self.assertTrue(self.text_area.is_editable())
            editable_state_button.click()
            self.assertFalse(self.text_area.is_editable())

        def test_text_area_get_window_text(self):
            self.assertEqual(text, self.text_area.window_text())

        def test_text_area_get_text_block(self):
            self.assertEqual(text, self.text_area.text_block())

        def test_text_area_line_count(self):
            self.assertEqual(self.text_area.line_count(), 3)

        def test_text_area_line_length(self):
            split_text = text.splitlines()
            for i, line in enumerate(split_text):
                self.assertEqual(self.text_area.line_length(i), len(line))

        def test_text_area_get_line(self):
            split_text = text.splitlines()
            for i, line in enumerate(split_text):
                self.assertEqual(self.text_area.get_line(i), line)

        def test_text_area_get_texts(self):
            self.assertEqual(self.text_area.texts(), text.splitlines())

        def test_text_area_get_selection_indices(self):
            self.assertEqual(self.text_area.selection_indices(), (len(text), len(text)))

        def test_text_area_set_text(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text)
            self.assertEqual(self.text_area.window_text(), new_text)

        def test_text_area_set_not_str(self):
            new_text = 111
            self.text_area.set_text(new_text)
            self.assertEqual(self.text_area.window_text(), str(new_text))

        def test_text_area_set_byte_str(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text.encode("utf-8"))
            self.assertEqual(self.text_area.window_text(), str(new_text))

        def test_text_area_set_text_at_start_position(self):
            new_text = "My new text\n"
            self.text_area.set_text(new_text, pos_start=0, pos_end=0)
            self.assertEqual(self.text_area.window_text(), new_text + text)

        def test_text_area_set_selection(self):
            self.text_area.select(0, 10)
            self.assertEqual(self.text_area.selection_indices(), (0, 10))

        def test_combobox_is_expanded(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertFalse(combo_box.is_expanded())

        def test_combobox_expand(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertFalse(combo_box.is_expanded())
            combo_box.expand()
            self.assertTrue(combo_box.is_expanded())

        def test_combobox_collapse(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.expand()
            self.assertTrue(combo_box.is_expanded())
            combo_box.collapse()
            self.assertFalse(combo_box.is_expanded())

        def test_combobox_texts(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.texts(), countries)

        def test_combobox_selected_text(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.selected_text(), countries[0])

        def test_combobox_selected_index(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.selected_index(), 0)

        def test_combobox_item_count(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            self.assertEqual(combo_box.item_count(), len(countries))

        def test_combobox_select_by_index(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.select(1)
            self.assertEqual(combo_box.selected_text(), countries[1])

        def test_combobox_select_by_text(self):
            combo_box = self.app_window.Frame.Panel.ComboBox
            combo_box.select(countries[1])
            self.assertEqual(combo_box.selected_text(), countries[1])

        def test_ololo(self):
            print_tree(self.app_window.element_info)
            combo_box = self.app_window.Frame.Panel.ComboBox
            time.sleep(5)
            print(combo_box.window_text())

            # actions = self.app_window.Frame.Panel.ComboBox.Menu.element_info.get_action()
            # print(actions.get_all_actions())

        def test_text_area_set_selection_by_text(self):
            text_to_select = "Select text"
            self.text_area.select(text_to_select)
            self.assertEqual(self.text_area.selection_indices(),
                             (text.find(text_to_select), text.find(text_to_select) + len(text_to_select)))

if __name__ == "__main__":
    unittest.main()
