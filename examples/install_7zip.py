"""
Install script for 7zip 9.20 (64-bit)

Requirements:
  - Win7 or Win8.1 x64, 64-bit Python
  - pywinauto 0.5.2+
  - 7z920-x64.msi is in the same folder as the script
  - UAC is fully disabled
"""
from __future__ import print_function
import sys, os
os.chdir(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
import pywinauto

app = pywinauto.Application().Start(r'msiexec.exe /i 7z920-x64.msi')

Wizard = app['7-Zip 9.20 (x64 edition) Setup']
Wizard.NextButton.click()

Wizard['I &accept the terms in the License Agreement'].wait('enabled').check_by_click()
Wizard.NextButton.click()

Wizard['Custom Setup'].wait('enabled')
Wizard.NextButton.click()

Wizard.Install.click()

Wizard.Finish.wait('enabled', timeout=30)
Wizard.Finish.click()
Wizard.wait_not('visible')

# final check
if os.path.exists(r"C:\Program Files\7-Zip\7zFM.exe"):
    print('OK')
else:
    print('FAIL')