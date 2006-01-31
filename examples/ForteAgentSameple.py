import time
from pprint import pprint

from pywinauto.application import Application

# start the application and wait for the Agent Dialog to be ready
app = Application().start_(r"c:\program files\agent\agent.exe")
app.Agent.WaitReady()

# if we get the Agent Setup wizard pops up close it
if app.AgentSetupWizard.Cancel.Exists():
    app.AgentSetupWizard.Cancel.Click()
    app.AgentSetupWizard2.Yes.Click()

# Select to emtpy trash
app.Agend.MenuSelect("File->EmptyTrash")
app.EmptyTrash.No.Click()

# Select some more menus (typo not important :-)
app.Agend.MenuSelect("File->Purge and Compact -> Compact All Folders")
app.Agent.OK.Click()

app.Agend.MenuSelect("File->Purge and Compact->PurgeFoldersInDesks")
app.PurgeFoldersInDesks.Cancel.Click()


# this is strange - when I do it by hand this is "Purge Folder" but during
# automation the text of the menu item is Purge Selected Folders
# FIXED - need to init the sub menu!
app.Agend.MenuSelect("File->Purge and Compact->Purge Folder")
app.AgentTip.OK.Click()

app.Agend.MenuSelect("File->Import and Export->Import Messages")
app.ImportMessages.Cancel.Click()

app.Agend.MenuSelect("File->Import and Export->Import Address Book")
app.ImportAddresses.Cancel.Click()

app.Agend.MenuSelect("File->Import and Export->Export Address Book")
app.ExportAddresses.Cancel.Click()

# pick something other then a file menu item
app.Agend.MenuSelect("Tools->ApplyFiltersToFolder")
app.AgentTip.OK.Click()
app.ApplyFiltersToFolders.Cancel.Click()


print "==" * 20
print "The Agent File Menu..."
print "==" * 20
pprint (app.Agent.MenuItems()[1])
app.Agent.MenuSelect("File->Print")
app.Print.Cancel.Click()

# quit Agent
app.Agent.MenuSelect("File -> Exit")
