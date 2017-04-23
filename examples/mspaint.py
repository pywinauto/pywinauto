"""
Example script for MS Paint

Requirements:
  - tested on Windows 10 (should work on Win7+)
  - pywinauto 0.6.1+

The example shows how to work with MS Paint application. It opens
JPEG image and resizes it using "Resize and Skew" dialog.
"""

from __future__ import print_function
import logging
from pywinauto import actionlogger
from pywinauto import Application

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--log", help = "enable logging", type=str, required = False)
args = parser.parse_args()

actionlogger.enable()
logger = logging.getLogger('pywinauto')
if args.log:
    logger.handlers[0] = logging.FileHandler(args.log)

app = Application(backend='uia').start(r'mspaint.exe')
dlg = app.window(title_re='.* - Paint')

# File->Open menu selection
dlg.File_tab.click()
dlg.child_window(title='Open', control_type='MenuItem', found_index=0).invoke()

# handle Open dialog
file_name_edit = dlg.Open.child_window(title="File name:", control_type="Edit")
file_name_edit.set_text('walter_cat.jpg')
# There are 2 Open buttons:
# dlg.Open.Open.click() will call drop down list of the file name combo box.
# The child_window statement is just copied from print_control_identifiers().
dlg.Open.child_window(title="Open", auto_id="1", control_type="Button").click()

dlg.ResizeButton.click()
dlg.ResizeAndSkew.Pixels.select()
if dlg.ResizeAndSkew.Maintain_aspect_ratio.get_toggle_state() != 1:
    dlg.ResizeAndSkew.Maintain_aspect_ratio.toggle()
dlg.ResizeAndSkew.HorizontalEdit1.set_text('100')
dlg.ResizeAndSkew.OK.click()

# Select menu "File->Save as->PNG picture"
dlg.File_tab.click()
dlg.SaveAsGroup.child_window(title="Save as", found_index=1).invoke()
dlg.child_window(title='PNG picture', found_index=0).invoke()
# Type output file name and save
dlg.SaveAs.File_name_ComboBox.Edit.set_text('walter_cat_resized.png')
dlg.SaveAs.Save.click()

if dlg.ConfirmSaveAs.exists():
    dlg.ConfirmSaveAs.Yes.click()

# Close application
dlg.close()
