#!/usr/bin/python3

from gi import require_version
require_version("Gtk", "3.0")

from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def _add_menubar(self):
        main_bar = Gtk.MenuBar()
        file_menu = Gtk.Menu()
        file_menu_dropdown = Gtk.MenuItem.new_with_label("File")
        file_new = Gtk.MenuItem.new_with_label("New")
        file_open = Gtk.MenuItem.new_with_label("Open")
        file_exit = Gtk.MenuItem.new_with_label("Exit")
        file_menu_dropdown.set_submenu(file_menu)
        file_menu.append(file_new)
        file_new.connect("activate", self.on_new_menuitem_activated)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(file_open)
        file_open.connect("activate", self.on_open_menuitem_activated)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(file_exit)
        file_exit.connect("activate", self.on_exit_menuitem_activated)
        file_menu.append(Gtk.SeparatorMenuItem())
        main_bar.append(file_menu_dropdown)
        return main_bar

    def on_new_menuitem_activated(self, menuitem):
        print("MenuItem New activated")
        return "MenuItem New activated"

    def on_open_menuitem_activated(self, menuitem):
        print("MenuItem Open activated")
        return "MenuItem Open activated"

    def on_exit_menuitem_activated(self, menuitem):
        print("MenuItem Exit activated")
        return "MenuItem Exit activated"

    def _add_list_store(self):
        list_store = Gtk.ListStore(int, str, str)
        store_data = [(1, "Tomato", "Red"),
                      (2, "Cucumber", "Green"),
                      (3, "Reddish", "Purple"),
                      (4, "Cauliflower", "White"),
                      (5, "Capsicum", "Yellow"),
                      (6, "Capsicum", "Green"),
                      (7, "Capsicum", "Red"),
                      (8, "Carrot", "Orange"),
                      (9, "Potato", "Yellow"),
                      (10, "Garlic", "White"),
                      (11, "Onion", "White"),
                      (12, "Green Onion", "Green"),
                      (13, "Basilic", "Green")]
        for item in store_data:
            list_store.append(list(item))
        table_data = Gtk.TreeView(model = list_store)
        for i, col_title in enumerate(["Id", "Name", "Color"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_title, renderer, text=i)
            table_data.append_column(column)

        scroll_window_list_store = Gtk.ScrolledWindow()
        # scroll_window_list_store.set_hexpand(True)
        scroll_window_list_store.add(table_data)
        return scroll_window_list_store

    def _add_tree(self, ):
        tree_store = Gtk.TreeStore(str)
        tree_store.append(None, ["Empty Date"])
        weeks = tree_store.append(None, ["Week"])
        week_data = [["Monday"], ["Tuesday"], ["Wednesday"], ["Thursday"], ["Friday"], ["Saturday"], ["Sunday"]]
        for i in range(len(week_data)):
            tree_store.append(weeks, week_data[i])
        months = tree_store.append(None, ["Month"])
        months_data = [["January"], ["February"], ["March"], ["April"], ["May"], ["June"], ["July"], ["August"],
                       ["September"], ["October"], ["November"], ["December"]]
        for i in range(len(months_data)):
            tree_store.append(months, months_data[i])
        years = tree_store.append(None, ["Year"])
        years_data = [["2019"], ["2020"], ["2021"], ["2022"]]
        for i in range(len(years_data)):
            tree_store.append(years, years_data[i])
        tree_view = Gtk.TreeView()
        tree_view.set_model(tree_store)
        cell_renderer_text = Gtk.CellRendererText()
        tree_view_column = Gtk.TreeViewColumn("Date Elements")
        tree_view.append_column(tree_view_column)
        tree_view_column.pack_start(cell_renderer_text, True)
        tree_view_column.add_attribute(cell_renderer_text, "text", 0)

        scroll_window_tree = Gtk.ScrolledWindow()
        #scroll_window_tree.set_hexpand(True)
        scroll_window_tree.add(tree_view)

        return scroll_window_tree

    def _add_listbox(self):
        listbox = Gtk.ListBox()
        for count in range(0, 9):
            label = Gtk.Label()
            label.set_text(f"TextItem {count}")
            listbox.add(label)
        return listbox

    def _add_header(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_title("Gtk Example Header")
        header_bar.set_subtitle("HeaderBar Subtitle")
        header_bar.set_show_close_button(True)
        button = Gtk.Button.new_with_label("Open")
        header_bar.pack_start(button)
        return header_bar

    def _add_levelbar(self):
        level_bar = Gtk.LevelBar()
        level_bar.set_min_value(0)
        level_bar.set_max_value(10)
        level_bar.set_value(7)
        return level_bar

    def _add_tab(self):
        page = Gtk.VBox(homogeneous=False, spacing=6)
        return page

    def _add_table(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(3)
        grid.set_column_spacing(3)
        table = Gtk.Table(n_rows=4, n_columns=5, homogeneous=False)
        first_column_label = Gtk.Label()
        first_column_label.set_text("/")
        second_column_label = Gtk.Label()
        second_column_label.set_text("A")
        third_column_label = Gtk.Label()
        third_column_label.set_text("B")
        fourth_column_label = Gtk.Label()
        fourth_column_label.set_text("C")
        fifth_column_label = Gtk.Label()
        fifth_column_label.set_text("D")
        table.attach(first_column_label, 0, 1, 0, 1)
        table.attach(second_column_label, 1, 2, 0, 1)
        table.attach(third_column_label, 2, 3, 0, 1)
        table.attach(fourth_column_label, 3, 4, 0, 1)
        table.attach(fifth_column_label, 4, 5, 0, 1)

        second_row_label = Gtk.Label()
        second_row_label.set_text("1")
        third_row_label = Gtk.Label()
        third_row_label.set_text("2")
        fourth_row_label = Gtk.Label()
        fourth_row_label.set_text("3")
        fifth_row_label = Gtk.Label()
        fifth_row_label.set_text("4")
        table.attach(second_row_label, 0, 1, 1, 2)
        table.attach(third_row_label, 0, 1, 2, 3)
        table.attach(fourth_row_label, 0, 1, 3, 4)
        table.attach(fifth_row_label, 0, 1, 4, 5)

        a1 = Gtk.TextView()
        a1_buffer = a1.get_buffer()
        a1_buffer.set_text("A1")
        table.attach(a1, 1, 2, 1, 2)
        a2 = Gtk.TextView()
        a2_buffer = a2.get_buffer()
        a2_buffer.set_text("A2")
        table.attach(a2, 1, 2, 2, 3)
        a3 = Gtk.TextView()
        a3_buffer = a3.get_buffer()
        a3_buffer.set_text("A3")
        table.attach(a3, 1, 2, 3, 4)
        a4 = Gtk.TextView()
        a4_buffer = a4.get_buffer()
        a4_buffer.set_text("A4")
        table.attach(a4, 1, 2, 4, 5)

        b1 = Gtk.TextView()
        b1_buffer = b1.get_buffer()
        b1_buffer.set_text("B1")
        table.attach(b1, 2, 3, 1, 2)
        b2 = Gtk.TextView()
        b2_buffer = b2.get_buffer()
        b2_buffer.set_text("B2")
        table.attach(b2, 2, 3, 2, 3)
        b3 = Gtk.TextView()
        b3_buffer = b3.get_buffer()
        b3_buffer.set_text("B3")
        table.attach(b3, 2, 3, 3, 4)
        b4 = Gtk.TextView()
        b4_buffer = b4.get_buffer()
        b4_buffer.set_text("B4")
        table.attach(b4, 2, 3, 4, 5)

        c1 = Gtk.TextView()
        c1_buffer = c1.get_buffer()
        c1_buffer.set_text("C1")
        table.attach(c1, 3, 4, 1, 2)
        c2 = Gtk.TextView()
        c2_buffer = c2.get_buffer()
        c2_buffer.set_text("C2")
        table.attach(c2, 3, 4, 2, 3)
        c3 = Gtk.TextView()
        c3_buffer = c3.get_buffer()
        c3_buffer.set_text("C3")
        table.attach(c3, 3, 4, 3, 4)
        c4 = Gtk.TextView()
        c4_buffer = c4.get_buffer()
        c4_buffer.set_text("C4")
        table.attach(c4, 3, 4, 4, 5)

        d1 = Gtk.TextView()
        d1_buffer = d1.get_buffer()
        d1_buffer.set_text("D1")
        table.attach(d1, 4, 5, 1, 2)
        d2 = Gtk.TextView()
        d2_buffer = d2.get_buffer()
        d2_buffer.set_text("D2")
        table.attach(d2, 4, 5, 2, 3)
        d3 = Gtk.TextView()
        d3_buffer = d3.get_buffer()
        d3_buffer.set_text("D3")
        table.attach(d3, 4, 5, 3, 4)
        d4 = Gtk.TextView()
        d4_buffer = d4.get_buffer()
        d4_buffer.set_text("D4")
        table.attach(d4, 4, 5, 4, 5)

        grid.set_column_homogeneous(True)
        grid.set_column_spacing(3)
        grid.set_row_spacing(3)
        grid.attach(table, 0, 0, 2, 3)

        layer = Gtk.Layout()
        grid.attach(layer, 2, 0, 1, 3)

        return grid

    def _add_grid_table(self):
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        first_column_label = Gtk.Label()
        first_column_label.set_text("/")
        second_column_label = Gtk.Label()
        second_column_label.set_text("A")
        third_column_label = Gtk.Label()
        third_column_label.set_text("B")
        fourth_column_label = Gtk.Label()
        fourth_column_label.set_text("C")
        fifth_column_label = Gtk.Label()
        fifth_column_label.set_text("D")
        grid.attach(first_column_label, 0, 0, 1, 1)
        grid.attach(second_column_label, 1, 0, 1, 1)
        grid.attach(third_column_label, 2, 0, 1, 1)
        grid.attach(fourth_column_label, 3, 0, 1, 1)
        grid.attach(fifth_column_label, 4, 0, 1, 1)

        second_row_label = Gtk.Label()
        second_row_label.set_text("1")
        third_row_label = Gtk.Label()
        third_row_label.set_text("2")
        fourth_row_label = Gtk.Label()
        fourth_row_label.set_text("3")
        fifth_row_label = Gtk.Label()
        fifth_row_label.set_text("4")
        grid.attach(second_row_label, 0, 1, 1, 1)
        grid.attach(third_row_label, 0, 2, 1, 1)
        grid.attach(fourth_row_label, 0, 3, 1, 1)
        grid.attach(fifth_row_label, 0, 4, 1, 1)

        a1 = Gtk.TextView()
        a1_buffer = a1.get_buffer()
        a1_buffer.set_text("A1")
        grid.attach(a1, 1, 1, 1, 1)
        a2 = Gtk.TextView()
        a2_buffer = a2.get_buffer()
        a2_buffer.set_text("A2")
        grid.attach(a2, 1, 2, 1, 1)
        a3 = Gtk.TextView()
        a3_buffer = a3.get_buffer()
        a3_buffer.set_text("A3")
        grid.attach(a3, 1, 3, 1, 1)
        a4 = Gtk.TextView()
        a4_buffer = a4.get_buffer()
        a4_buffer.set_text("A4")
        grid.attach(a4, 1, 4, 1, 1)

        b1 = Gtk.TextView()
        b1_buffer = b1.get_buffer()
        b1_buffer.set_text("B1")
        grid.attach(b1, 2, 1, 1, 1)
        b2 = Gtk.TextView()
        b2_buffer = b2.get_buffer()
        b2_buffer.set_text("B2")
        grid.attach(b2, 2, 2, 1, 1)
        b3 = Gtk.TextView()
        b3_buffer = b3.get_buffer()
        b3_buffer.set_text("B3")
        grid.attach(b3, 2, 3, 1, 1)
        b4 = Gtk.TextView()
        b4_buffer = b4.get_buffer()
        b4_buffer.set_text("B4")
        grid.attach(b4, 2, 4, 1, 1)

        c1 = Gtk.TextView()
        c1_buffer = c1.get_buffer()
        c1_buffer.set_text("C1")
        grid.attach(c1, 3, 1, 1, 1)
        c2 = Gtk.TextView()
        c2_buffer = c2.get_buffer()
        c2_buffer.set_text("C2")
        grid.attach(c2, 3, 2, 1, 1)
        c3 = Gtk.TextView()
        c3_buffer = c3.get_buffer()
        c3_buffer.set_text("C3")
        grid.attach(c3, 3, 3, 1, 1)
        c4 = Gtk.TextView()
        c4_buffer = c4.get_buffer()
        c4_buffer.set_text("C4")
        grid.attach(c4, 3, 4, 1, 1)

        d1 = Gtk.TextView()
        d1_buffer = d1.get_buffer()
        d1_buffer.set_text("D1")
        grid.attach(d1, 4, 1, 1, 1)
        d2 = Gtk.TextView()
        d2_buffer = d2.get_buffer()
        d2_buffer.set_text("D2")
        grid.attach(d2, 4, 2, 1, 1)
        d3 = Gtk.TextView()
        d3_buffer = d3.get_buffer()
        d3_buffer.set_text("D3")
        grid.attach(d3, 4, 3, 1, 1)
        d4 = Gtk.TextView()
        d4_buffer = d4.get_buffer()
        d4_buffer.set_text("D4")
        grid.attach(d4, 4, 4, 1, 1)

        return grid

    def _add_scrollbar(self, grid):
        layout = Gtk.Layout()
        layout.set_size(300, 200)
        layout.set_vexpand(True)
        layout.set_hexpand(True)
        layout.put(self.notebook, 10, 10)
        grid.attach(layout, 1, 1, 1, 1)
        vadjustment = layout.get_vadjustment()
        vscrollbar = Gtk.VScrollbar(orientation=Gtk.Orientation.VERTICAL,
                                   adjustment=vadjustment)
        grid.attach(vscrollbar, 4, 1, 1, 1)

    def __init__(self):
        Gtk.Window.__init__(self, title="MainWindow")

        self.set_decorated(True)
        self.notebook = Gtk.Notebook()
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(5)
        self.grid.set_column_spacing(5)
        self.add(self.grid)
        self.set_default_size(600, 200)
        self.set_border_width(0)
        self._add_scrollbar(self.grid)

        general_tab = self._add_tab()
        self.notebook.append_page(general_tab, Gtk.Label.new("General"))
        tree_tab = self._add_tab()
        self.notebook.append_page(tree_tab, Gtk.Label.new("Tree"))
        list_store_tab = self._add_tab()
        self.notebook.append_page(list_store_tab, Gtk.Label.new("List Views"))
        tree_tab.add(self._add_tree())
        list_store_tab.add(self._add_list_store())

        listbox_tab = self._add_tab()
        self.notebook.append_page(listbox_tab, Gtk.Label.new("ListBox and Grid"))
        int_grid = Gtk.Grid()
        int_grid.set_row_spacing(3)
        int_grid.set_column_spacing(5)
        int_grid.set_column_homogeneous(True)
        separator = Gtk.Separator()
        separator.new(Gtk.Orientation(1))
        listbox_tab.add(int_grid)
        int_grid.attach(self._add_listbox(), 1, 1, 1, 1)
        int_grid.attach(separator, 2, 1, 1, 1)
        int_grid.attach(self._add_grid_table(), 3, 1, 1, 1)
        self.set_titlebar(self._add_header())

        table_tab = self._add_tab()
        self.notebook.append_page(table_tab, Gtk.Label.new("Table"))
        table_tab.add(self._add_table())
        self.grid.attach(self._add_menubar(), 0, 0, 5, 1)


win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
