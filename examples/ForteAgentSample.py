import time
from pprint import pprint

from pywinauto.application import Application

# start the application and wait for the Agent Dialog to be ready
app = Application().start_(r"c:\program files\agent\agent.exe")

# if the trial nag dialog pops up
if app.ForteAgentTrial.Exists():
    app.ForteAgentTrial.IdLikeToContinueUsingAgentfor7moredays.Click()
    app.ForteAgentTrial.OK.Click()

# wait until the app is ready
app.Agent.WaitReady()

# if we get the Agent Setup wizard pops up close it
if app.AgentSetupWizard.Cancel.Exists():
    app.AgentSetupWizard.Cancel.Click()
    app.AgentSetupWizard2.Yes.Click()

# Select to emtpy trash
app.Agent.MenuSelect("File->EmptyTrash")
app.EmptyTrash.No.Click()

# Select some more menus (typo not important :-)
app.Agent.MenuSelect("File->Purge and Compact -> Compact All Folders")
app.Agent.OK.Click()

app.Agent.MenuSelect("File->Purge and Compact->PurgeFoldersInDesks")
app.PurgeFoldersInDesks.Cancel.Click()


# this is strange - when I do it by hand this is "Purge Folder" but during
# automation the text of the menu item is Purge Selected Folders
# FIXED - need to init the sub menu!
app.Agent.MenuSelect("File->Purge and Compact->Purge Folder")
app.AgentTip.OK.Click()

app.Agent.MenuSelect("File->Import and Export->Import Messages")
app.ImportMessages.Cancel.Click()

app.Agent.MenuSelect("File->Import and Export->Import Address Book")
app.ImportAddresses.Cancel.Click()

app.Agent.MenuSelect("File->Import and Export->Export Address Book")
app.ExportAddresses.Cancel.Click()

# pick something other then a file menu item
app.Agent.MenuSelect("Tools->ApplyFiltersToFolder")
app.AgentTip.OK.Click()
app.ApplyFiltersToFolders.Cancel.Click()


print "==" * 20
print "The Agent File Menu..."
print "==" * 20
pprint (app.Agent.MenuItems()[1])
try:
    app.Agent.MenuSelect("File->Print")
    app.Print.Cancel.Click()
except:
    print "Print Menu was probably disabled"

# quit Agent
app.Agent.MenuSelect("File -> Exit")
