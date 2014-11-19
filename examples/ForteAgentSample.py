"""Perform some tests with Forte Agent

NOTE: Forte Agent has a very dynamic interface
e.g. whether it is free or not, whether it is still in the grace
period. For this reason this example script may or may not work well
for you"""

print __doc__

import time
from pprint import pprint

from pywinauto.application import Application

# start the application and wait for the Agent Dialog to be ready
app = Application().start_(r"c:\program files\agent\agent.exe")

while not app.Windows_():
    time.sleep(.5)

# if the trial nag dialog pops up
if app.window_(title = "Forte Agent Trial").Exists():
    #app.ForteAgentTrial.IdLikeToContinueUsingAgentfor7moredays.Click()
    app.ForteAgentTrial.IdliketouseFreeAgent
    app.ForteAgentTrial.OK.Click()

if app.window_(title = "Free Agent Registration").Exists():
    app.FreeAgentRegistration.ImreallybusyRemindmein30.Click()
    app.FreeAgentRegistration.OK.CloseClick()

if app.window_(title = "What's New Reminder").Exists():
    app.WhatsNewReminder.ImreallybusyRemindmein90.Click()
    app.WhatsNewReminder.OK.CloseClick()



# wait until the app is ready
app.FreeAgent.Wait("ready")

# if we get the Agent Setup wizard pops up close it
if app.AgentSetupWizard.Cancel.Exists(1):
    app.AgentSetupWizard.Cancel.Click()
    app.AgentSetupWizard2.Yes.Click()

# Select to emtpy trash
app.FreeAgent.MenuSelect("File->EmptyTrash")
app.EmptyTrash.No.Click()

# Select some more menus (typo not important :-)
app.FreeAgent.MenuSelect("File->Purge and Compact -> Compact All Folders")
app.FreeAgent.OK.Click()

#print app.FreeAgent.MenuItem("File->Purge and compact").GetProperties()
#app.FreeAgent.MenuSelect("File->Purge and Compact->PurgeFolder")
#app.PurgeFoldersInDesks.Cancel.Click()


# this is strange - when I do it by hand this is "Purge Folder" but during
# automation the text of the menu item is Purge Selected Folders
# FIXED - need to init the sub menu!
app.FreeAgent.MenuSelect("File->Purge and Compact->Purge Folder")
app.AgentTip.OK.Click()

app.FreeAgent.MenuSelect("File->Import and Export->Import Messages")
app.ImportMessages.Cancel.Click()

app.FreeAgent.MenuSelect("File->Import and Export->Import Address Book")
app.ImportAddresses.Cancel.Click()

app.FreeAgent.MenuSelect("File->Import and Export->Export Address Book")
app.ExportAddresses.Cancel.Click()

# pick something other then a file menu item
app.FreeAgent.MenuSelect("Tools->ApplyFiltersToFolder")
if app.ToolsApplyFilters.OK.Exists():
    app.ToolsApplyFilters.OK.Click()

#app.AgentTip.OK.Click()
#app.ApplyFiltersToFolders.Cancel.Click()


print "==" * 20
print "The Agent File Menu..."
print "==" * 20
pprint (app.FreeAgent.MenuItems()[1])
try:
    app.FreeAgent.MenuSelect("File->Print")
    app.Print.Cancel.Click()
except:
    print "Print Menu was probably disabled"

# quit Agent
app.FreeAgent.MenuSelect("File -> Exit")
