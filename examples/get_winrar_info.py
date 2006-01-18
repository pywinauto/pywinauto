"""Automate WinRAR evaluation copy

We hit a few dialogs and save XML dump and 
screenshot from each dialog.

Specify a language at the command line:
	0 Czech
	1 German
	2 French
	
More then likely you will need to modify the apppath
entry in the 't' dictionary to where you have
extracted the WinRAR executables.
"""

import sys

from pywinauto.application import Application
import time

folders = ['wrar351cz', 'wrar351d', 'wrar351fr']

# translations for each language
t = {
	'apppath' : (
		'c:\.temp\wrar351fr\winrar.exe',
		'c:\.temp\wrar351d\winrar.exe',
		'c:\.temp\wrar351cz\winrar.exe'
	),

	# Buy Licence Dialog
	'Buy Licence' : (
		"Acheter une licence pur winRAR", 
		"Bittekaufensieeine", 
		"Zakuptesiprosm"),
	'Close' : (
		"Fermer", 
		"Schleissen", 
		"Zavrit"),

	# Options->Configure menu items
	"Options->Configure" : (
		"Options->Configuration", 
		"Optionen->Einstellungen", 
		"Moznosti->Nastaveni"),

	# Configure/Options dialog box
	'Configure' : (
		"Configuration", 
		"Einstellungen", 
		"Nastaveni"),	

	# personalise toolbar buttons button
	'Buttons' : (
		"Boutons", 
		"Schaltflachen", 
		"Vybrattlacitka"),

	# Personalize toolbars dialog	
	'PeronnaliseToolbars' : (
		"Peronnalisation de la barre doutils", 
		"Werkzeugleisteanpassen", 
		"Vybertlaciteknastrojovelisty"),
	
	# create profile button
	'CreateDefaultProfile' : (
		u"Creerleprofilpardéfault", 
		"Standardfestlegen", 
		"Vytvoritimplicitni"),
	
	# create profile dialog box title
	'ConfigureDefaultOptions' : (
		"Configurer les options de compre...", 
		"Standardkomprimierungs", 
		"Zmenaimplicitnichnast..."),
		
	# context menu's button
	"ContextMenus" :  (
		"Menus contextuels", 
		"Optionenimkontextmenu", 
		"Polozkykontextovehamenu"),
	
	# context menu's dialog
	"contextMenuDlg" :  (
		"Rubriques des menus contextuels", 
		"OptionenindenKontextmenus", 
		"Polozkykontextovehamenu"),
	
	# file->exit menu option
	"File->Exit" : (
		"Fichier->Quitter", 
		"Datei->Beenden", 
		"Soubor->Konec"),
}



def get_winrar_dlgs(rar_dlg, x):
	rar_dlg.MenuSelect(t["Options->Configure"][x])
	
	optionsdlg = rar_dlg.app[t['Configure'][x]]
	optionsdlg._write("Options_%d.xml"%x)
	optionsdlg.CaptureAsImage().save("Options_%d.png"%x)
	optionsdlg[t['Buttons'][x]].Click()
	
	contextMenuDlg = rar_dlg.app[t['PeronnaliseToolbars'][x]]
	contextMenuDlg._write("PersonaliseToolbars_%d.xml"%x)
	contextMenuDlg.CaptureAsImage().save("PersonaliseToolbars_%d.png"%x)
	contextMenuDlg.OK.Click()

	optionsdlg.TabCtrl.Select(1)
	optionsdlg[t['CreateDefaultProfile'][x]].Click()
	
	defaultOptionsDlg = rar_dlg.app[t['ConfigureDefaultOptions'][x]]
	defaultOptionsDlg._write("DefaultOptions_%d.xml"%x)
	defaultOptionsDlg.CaptureAsImage().save("DefaultOptions_%d.png"%x)
	defaultOptionsDlg.OK.Click()
	
	optionsdlg.TabCtrl.Select(6)
	optionsdlg[t['ContextMenus'][x]].Click()
	
	anotherMenuDlg = rar_dlg.app[t['contextMenuDlg'][x]]
	anotherMenuDlg._write("2ndMenuDlg_%d.xml"%x)
	anotherMenuDlg.CaptureAsImage().save("2ndMenuDlg_%d.png"%x)
	
	anotherMenuDlg.OK.Click()
	
	optionsdlg.OK.Click()
	
	
# get the languages as an integer
x = int(sys.argv[1])

# start the application
app = Application()._start(t['apppath'][x])

# we have to wait for the Licence Dialog to open
time.sleep(2)

# close the Buy licence dialog box
licence_dlg = app[t['Buy Licence'][x]]
licence_dlg[t['Close'][x]].Click()

# find the WinRar main dialog
rar_dlg = app._window(title_re = ".* - WinRAR.*")

# dump and capture some dialogs
get_winrar_dlgs(rar_dlg, x)

# exit WinRar
rar_dlg.MenuSelect(t['File->Exit'][x])
