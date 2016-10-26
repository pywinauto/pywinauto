"""
Uninstall script for 7zip 9.20 (64-bit)

Requirements:
  - Win7 or Win8.1 x64, 64-bit Python
  - pywinauto 0.5.2+
  - UAC is fully disabled
"""
from __future__ import print_function
import pywinauto

pywinauto.Application().Start(r'explorer.exe')
explorer = pywinauto.Application().Connect(path='explorer.exe')

# Go to "Control Panel -> Programs and Features"
NewWindow = explorer.window(top_level_only=True, active_only=True, class_name='CabinetWClass')
try:
    NewWindow.AddressBandRoot.click_input()
    NewWindow.type_keys(r'Control Panel\Programs\Programs and Features{ENTER}',
                        with_spaces=True, set_foreground=False)
    ProgramsAndFeatures = explorer.window(top_level_only=True, active_only=True,
                                          title='Programs and Features', class_name='CabinetWClass')

    # wait while the list of programs is loading
    explorer.wait_cpu_usage_lower(threshold=5)

    item_7z = ProgramsAndFeatures.FolderView.get_item('7-Zip 9.20 (x64 edition)')
    item_7z.ensure_visible()
    item_7z.click_input(button='right', where='icon')
    explorer.PopupMenu.menu_item('Uninstall').click()

    Confirmation = explorer.window(title='Programs and Features', class_name='#32770', active_only=True)
    if Confirmation.Exists():
        Confirmation.Yes.click_input()
        Confirmation.wait_not('visible')

    WindowsInstaller = explorer.window(title='Windows Installer', class_name='#32770', active_only=True)
    if WindowsInstaller.Exists():
        WindowsInstaller.wait_not('visible', timeout=20)

    SevenZipInstaller = explorer.window(title='7-Zip 9.20 (x64 edition)', class_name='#32770', active_only=True)
    if SevenZipInstaller.Exists():
        SevenZipInstaller.wait_not('visible', timeout=20)

    if '7-Zip 9.20 (x64 edition)' not in ProgramsAndFeatures.FolderView.texts():
        print('OK')
finally:
    NewWindow.close()