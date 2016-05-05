"""
Script for display user groups and users in group Administrators

Requirements: Python 2.7 or 3.4, pyWin32, pywinauto 0.5.3+
 download the repo: https://github.com/pywinauto/pywinauto
 place the script to the repo root folder
"""
from subprocess import Popen
from pywinauto import application
from pywinauto.timings import always_wait_until_passes


def is_user_an_admin():
    import os
    if os.name == 'nt':
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
        except:
            return os.environ['USERNAME'], False
        else:
            return os.environ['USERNAME'], True
    else:
        if 'SUDO_USER' in os.environ and os.geteuid() == 0:
            return os.environ['SUDO_USER'], True
        else:
            return os.environ['USERNAME'], False


if is_user_an_admin():
    Popen(['compmgmt.msc'], shell=True)


    @always_wait_until_passes(4, 2, application.ProcessNotFoundError)
    def connect_to_mmc():
        return application.Application().connect(path="mmc.exe")


    app = connect_to_mmc()
    tree = app.mmc_main_frame.tree_view
    groups = tree.get_item(r'\Computer Management (Local)\System Tools\Local Users and Groups\Groups')
    groups.click()
    items = app.mmc_main_frame.list_view.items()
    print('Groups and descriptions:')
    for element in items:
        print(element.text())
    try:
        administrators = app.mmc_main_frame.list_view.get_item('Administrators')
        administrators.click(double=True)  # double click opens group properties
        items = app.dialog.list_view.items()
        print('Administrators:')
        for element in items:
            print(element.text())
    except:
        print('There is no Administrators group')
else:
    print('You are not administrator')
