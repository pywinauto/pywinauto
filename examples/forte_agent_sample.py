"""Perform some tests with Forte Agent

NOTE: Forte Agent has a very dynamic interface
e.g. whether it is free or not, whether it is still in the grace
period. For this reason this example script may or may not work well
for you"""
from __future__ import print_function

print(__doc__)

import time
from pprint import pprint

from pywinauto.application import Application

# start the application and wait for the Agent Dialog to be ready
app = Application().start(r"c:\program files\agent\agent.exe")

while not app.Windows_():
    time.sleep(.5)

# if the trial nag dialog pops up
if app.window(title = "Forte Agent Trial").Exists():
    #app.ForteAgentTrial.IdLikeToContinueUsingAgentfor7moredays.click()
    app.ForteAgentTrial.IdliketouseFreeAgent.check()
    app.ForteAgentTrial.OK.click()

if app.window(title = "Free Agent Registration").Exists():
    app.FreeAgentRegistration.ImreallybusyRemindmein30.click()
    app.FreeAgentRegistration.OK.close_click()

if app.window(title = "What's New Reminder").Exists():
    app.WhatsNewReminder.ImreallybusyRemindmein90.click()
    app.WhatsNewReminder.OK.close_click()



# wait until the app is ready
app.FreeAgent.wait("ready")

# if we get the Agent Setup wizard pops up close it
if app.AgentSetupWizard.Cancel.Exists(1):
    app.AgentSetupWizard.Cancel.click()
    app.AgentSetupWizard2.Yes.click()

# Select to emtpy trash
app.FreeAgent.menu_select("File->EmptyTrash")
app.EmptyTrash.No.click()

# Select some more menus (typo not important :-)
app.FreeAgent.menu_select("File->Purge and Compact -> Compact All Folders")
app.FreeAgent.OK.click()

#print app.FreeAgent.menu_item("File->Purge and compact").get_properties()
#app.FreeAgent.menu_select("File->Purge and Compact->PurgeFolder")
#app.PurgeFoldersInDesks.Cancel.click()


# this is strange - when I do it by hand this is "Purge Folder" but during
# automation the text of the menu item is Purge Selected Folders
# FIXED - need to init the sub menu!
app.FreeAgent.menu_select("File->Purge and Compact->Purge Folder")
app.AgentTip.OK.click()

app.FreeAgent.menu_select("File->Import and Export->Import Messages")
app.ImportMessages.Cancel.click()

app.FreeAgent.menu_select("File->Import and Export->Import Address Book")
app.ImportAddresses.Cancel.click()

app.FreeAgent.menu_select("File->Import and Export->Export Address Book")
app.ExportAddresses.Cancel.click()

# pick something other then a file menu item
app.FreeAgent.menu_select("Tools->ApplyFiltersToFolder")
if app.ToolsApplyFilters.OK.Exists():
    app.ToolsApplyFilters.OK.click()

#app.AgentTip.OK.click()
#app.ApplyFiltersToFolders.Cancel.click()


print("==" * 20)
print("The Agent File Menu...")
print("==" * 20)
pprint (app.FreeAgent.menu_items()[1])
try:
    app.FreeAgent.menu_select("File->Print")
    app.Print.Cancel.click()
except Exception:
    print("Print Menu was probably disabled")

# quit Agent
app.FreeAgent.menu_select("File -> Exit")
