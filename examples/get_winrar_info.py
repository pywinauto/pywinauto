import sys

from application import Application
import time

folders = ['wrar351cz', 'wrar351d', 'wrar351fr']


t = {
	'apppath' : (
		'c:\.temp\wrar351fr\winrar.exe',
		'c:\.temp\wrar351d\winrar.exe',
		'c:\.temp\wrar351cz\winrar.exe'
	),

	'Buy Licence' : (
		"Acheter une licence pur winRAR", 
		"Bittekaufensieeine", 
		"Zakuptesiprosm"),

	'Close' : (
		"Fermer", 
		"Schleissen", 
		"Zavrit"),


	"Options->Configure" : (
		"Options->Configuration", 
		"Optionen->Einstellungen", 
		"Moznosti->Nastaveni"),

	
	'Configure' : (
		"Configuration", 
		"Einstellungen", 
		"Nastaveni"),

	
	'Buttons' : (
		"Boutons", 
		"Schaltflachen", 
		"Vybrattlacitka"),
	
	'PeronnaliseToolbars' : (
		"Peronnalisation de la barre doutils", 
		"Werkzeugleisteanpassen", 
		"Vybertlaciteknastrojovelisty"),
	
	'CreateDefaultProfile' : (
		u"Creerleprofilpardéfault", 
		"Standardfestlegen", 
		"Vytvoritimplicitni"),
	
	'ConfigureDefaultOptions' : (
		"Configurer les options de compre...", 
		"Standardkomprimierungs", 
		"Zmenaimplicitnichnast..."),
		
	"ContextMenus" :  (
		"Menus contextuels", 
		"Optionenimkontextmenu", 
		"Polozkykontextovehamenu"),
		
	"contextMenuDlg" :  (
		"Rubriques des menus contextuels", 
		"OptionenindenKontextmenus", 
		"Polozkykontextovehamenu"),
		
	"File->Exit" : (
		"Fichier->Quitter", 
		"Datei->Beenden", 
		"Soubor->Konec"),
	




}

#
#[t['ConfigureDefaultOptions'][x]]
#[t['Close'][x]]
#[t['Buy Licence'][x]]
#[t['ContextMenus'][x]]
#
#
#[t['ContextMenus'][x]]
#

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
	defaultOptionsDlg._write("DefaultOptions_%1.xml"%x)
	defaultOptionsDlg.CaptureAsImage().save("DefaultOptions_%d.png"%x)
	defaultOptionsDlg.OK.Click()
	
	optionsdlg.TabCtrl.Select(6)
	optionsdlg[t['ContextMenus'][x]].Click()
	
	anotherMenuDlg = rar_dlg.app[t['contextMenuDlg'][x]]
	anotherMenuDlg._write("2ndMenuDlg_%d.xml"%x)
	anotherMenuDlg.CaptureAsImage().save("2ndMenuDlg_%d.png"%x)
	
	anotherMenuDlg.OK.Click()
	
	optionsdlg.OK.Click()
	
	

x = int(sys.argv[1])
app = Application()._start(t['apppath'][x])

# we have to wait for the Licence Dialog to open
time.sleep(2)
licence_dlg = app[t['Buy Licence'][x]]
licence_dlg[t['Close'][x]].Click()


rar_dlg = app._window(title_re = ".* - WinRAR.*")

get_winrar_dlgs(rar_dlg, x)

rar_dlg.MenuSelect(t['File->Exit'][x])
