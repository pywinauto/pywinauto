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
__revision__ = "$Revision$"

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
        "Zakuptesiprosmlicenci WinRARu"),
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



def get_winrar_dlgs(rar_dlg, app, lang):
    rar_dlg.MenuSelect(t["Options->Configure"][lang])

    optionsdlg = app[t['Configure'][lang]]

    optionsdlg.WriteToXML("Options_%d.xml"%lang)

    optionsdlg.CaptureAsImage().save("Options_%d.png"%lang)
    optionsdlg[t['Buttons'][lang]].Click()

    contextMenuDlg = app[t['PeronnaliseToolbars'][lang]]
    contextMenuDlg.WriteToXML("PersonaliseToolbars_%d.xml"%lang)
    contextMenuDlg.CaptureAsImage().save("PersonaliseToolbars_%d.png"%lang)
    contextMenuDlg.OK.Click()

    optionsdlg.TabCtrl.Select(1)
    optionsdlg[t['CreateDefaultProfile'][lang]].Click()

    defaultOptionsDlg = app[t['ConfigureDefaultOptions'][lang]]
    defaultOptionsDlg.WriteToXML("DefaultOptions_%d.xml"%lang)
    defaultOptionsDlg.CaptureAsImage().save("DefaultOptions_%d.png"%lang)
    defaultOptionsDlg.OK.Click()

    optionsdlg.TabCtrl.Select(6)
    optionsdlg[t['ContextMenus'][lang]].Click()

    anotherMenuDlg = app[t['contextMenuDlg'][lang]]
    anotherMenuDlg.WriteToXML("2ndMenuDlg_%d.xml"%lang)
    anotherMenuDlg.CaptureAsImage().save("2ndMenuDlg_%d.png"%lang)

    anotherMenuDlg.OK.Click()

    optionsdlg.OK.Click()


# get the languages as an integer
langs = [int(arg) for arg in sys.argv[1:]]

for lang in langs:
    # start the application
    app = Application().start_(t['apppath'][lang])

    # we have to wait for the Licence Dialog to open
    time.sleep(2)

    # close the Buy licence dialog box
    licence_dlg = app[t['Buy Licence'][lang]]
    licence_dlg[t['Close'][lang]].Click()

    # find the WinRar main dialog
    rar_dlg = app.window_(title_re = ".* - WinRAR.*")

    # dump and capture some dialogs
    get_winrar_dlgs(rar_dlg, app,  lang)

    # exit WinRar
    time.sleep(.5)
    rar_dlg.MenuSelect(t['File->Exit'][lang])
