from subprocess import Popen
from pywinauto import application
import time

Popen(['compmgmt.msc'], shell = True)

app = application.Application().connect(path="mmc.exe")
tree = app.mmc_main_frame.tree_view
groups = tree.get_item(r'\Computer Management (Local)\System Tools\Local Users and Groups\Groups')
groups.Click(double=True)
items = app.mmc_main_frame.list_view.items()
print('Groups and descriptions:')
for element in items:
    print(element.text())
app.window_specification.wait
administrators = app.mmc_main_frame.list_view.get_item('Administrators')
administrators.click(double=True)
items = app.dialog.list_view.items()
print('Administrators:')
for element in items:
    print(element.text())
