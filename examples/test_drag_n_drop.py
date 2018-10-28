"""
Example for drag-n-drop (DragMouseInput works, DragMouse crashes because of the bug in test app)

Requirements: Python 2.7 or 3.4, pyWin32, pywinauto 0.5.0+
 download the repo: https://github.com/pywinauto/pywinauto
 place the script to the repo root folder
"""
import sys, os

os.chdir(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0]))) # running at repo root folder
import pywinauto

mfc_samples_folder = os.path.join(
   os.path.dirname(sys.argv[0]), r"apps\MFC_samples")
if pywinauto.sysinfo.is_x64_Python():
    mfc_samples_folder = os.path.join(mfc_samples_folder, 'x64')

app = pywinauto.Application().start(os.path.join(mfc_samples_folder,
                                                 u"CmnCtrl1.exe"))

tree = app.Common_Controls_Sample.TreeView.WrapperObject()

birds = tree.get_item(r'\Birds')
dogs = tree.get_item(r'\Dogs')

# drag-n-drop without focus on the window
#tree.drag_mouse("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())

# most natural drag-n-drop (with real moving mouse, like real user)
tree.drag_mouse_input("left", birds.rectangle().mid_point(), dogs.rectangle().mid_point())
