"""
Script to display all the user groups and all the users in Administrators group

Requirements: Python 2.7 or 3.4, pyWin32, pywinauto 0.5.4+
 download the repo: https://github.com/pywinauto/pywinauto
 place the script to the repo root folder
"""
from subprocess import Popen
from pywinauto import application
from pywinauto.timings import always_wait_until_passes


class AccessDeniedError(Exception):
    """Raise when current user is not an administrator."""
    def __init__(self, arg):
        self.args = arg


class NoExistGroupError(Exception):
    """Raise when group Administrators is not exist."""
    def __init__(self, arg):
        self.args = arg


def is_user_an_admin():
    """ Check user admin """
    import os
    if os.name == 'nt':
        try:
            # only windows users with admin privileges can read the C:\windows\temp
            os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
        except Exception:
            return False
        else:
            return True
    else:
        return 'SUDO_USER' in os.environ and os.geteuid() == 0


if is_user_an_admin():
    Popen(['compmgmt.msc'], shell=True)


    @always_wait_until_passes(4, 2, application.ProcessNotFoundError)
    def connect_to_mmc():
        """ Returns connect app to instance """
        return application.Application().connect(path="mmc.exe")


    app = connect_to_mmc()
    tree = app.mmc_main_frame.tree_view
    groups = tree.get_item(r'\Computer Management (Local)\System Tools\Local Users and Groups\Groups')
    groups.click()
    items = app.mmc_main_frame.list_view.items()
    print('\nGroups:')
    for i in range(0, len(items), 2):
        print(items[i].text())
    try:
        administrators = app.mmc_main_frame.list_view.get_item('Administrators')
        administrators.click(double=True)  # double click opens group properties
        app.dialog.wait('exists')
        items = app.dialog.list_view.items()
        print('\nAdministrators:')
        for element in items:
            print(element.text())
    except ValueError:
        print('\nThere is no Administrators group')
    app.kill()
else:
    print('\nYou are not an administrator')
