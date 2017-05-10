"""
Example script for parce Google Drive files and folders with IE11

Requirements:
  - Internet Explorer 11 (tested on IE 11.0.9600.18537)
  - tested on Windows 7 SP1 (should work on Win7+)
  - pywinauto 0.6.1+
The example shows how to work with IE 11. It login to
Google Drive and parse files and folders names, then
saves them to file listdir.txt

"""

import os
import time
from os.path import expanduser
from pywinauto import Application
from pywinauto.keyboard import SendKeys

iexplorer_dir = r'"C:\Program Files\Internet Explorer\iexplore.exe"'

# # start google chrome
iexplorer = Application(backend='uia')
iexplorer.start(iexplorer_dir + ' https://accounts.google.com/signin/v2/identifier?service=wise&passive=true&continue=http%3A%2F%2Fdrive.google.com%2F%3Futm_source%3Den_US&utm_medium=button&utm_campaign=web&utm_content=gotodrive&usp=gtd&ltmpl=drive&urp=http%3A%2F%2Fsignin.co%2Fgoogle-drive%2F&flowName=GlifWebSignIn&flowEntry=ServiceLogin')

iexplorer.window().wait('ready', timeout=10)

# log in
iexplorer.window().type_keys('TestPywinauto{ENTER}')  # username

time.sleep(2)

iexplorer.window().type_keys('testpywinauto123{ENTER}')  # password

time.sleep(4)

SendKeys('^s')
time.sleep(2)

filename = 'google_drive_main_page'

# enter the page html file name
SendKeys(filename)

# select html and click OK
SendKeys('{TAB}{DOWN}{DOWN}{ENTER}{ENTER}')

time.sleep(2)

docPath = expanduser("~") + '\\Documents\\'
filepath = docPath + filename + '.htm'

def parseObjectsNames(filepath):
    lineWithNames = ''
    with open(filepath) as f:
        for line in f:
            if line.find('id="base-js"', 20, 40) > 0:
                lineWithNames = line
                break

    pos = lineWithNames.find('_DRIVE_ivd')
    lineWithNames = lineWithNames[pos + 16:]

    pos = lineWithNames.find("'")
    lineWithNames = lineWithNames[:pos - 2]

    lineWithNames = '[[[[[' + lineWithNames

    eol = False
    pos = 0
    names = []
    while eol == False:
        for _ in range(1, 9, 1):
            pos = lineWithNames.find("[", pos + 1)
            if pos < 0:
                eol = True
                break

        if not eol:
            pos = lineWithNames.find(',', pos)
            lineWithNames = lineWithNames[pos + 5:]

            pos = lineWithNames.find('\\')
            name = lineWithNames[:pos]

            if name.count(',') < 10:
                names.append(name)
            else:
                break
    return names


names = parseObjectsNames(filepath)

f = open('listdir.txt', 'w')
for name in names:
    f.write(name + '\n')
f.close()

os.remove(filepath)

#log out
for i in range(18):
    SendKeys('{TAB}')
SendKeys('{ENTER}' )
SendKeys('{TAB}{TAB}{TAB}{TAB}{ENTER}')

time.sleep(4)

#close active window
SendKeys('%{F4}')

print('DONE')

