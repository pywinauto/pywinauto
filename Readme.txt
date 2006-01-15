Unzip the Zip file

Copy (though you could move also) Python24.dll, dlgchecks2.dll and move 
PythonConfig.py to the folder that contains your executable (Silktest 
directory).
Modify PythonConfig.py to point to where you have unzipped the other 
files (this folder should contain all the *.py files and the Python24.zip 
file.

If your machine does not have the appropriate Visual Studio 7 DLLs you 
will also need these in the executable directory. (Included in the Zip 
in RequiredDLLs).


There is also a little sample FindDialog.exe application (it does not use 
the DLL - but the underlying Python libraries). What it does is perform most 
of the tests (it doesn't do AllControls or AsianHotkeyTests) and highlights 
controls with errors with a red rectangle.

Mostly you need to run this dialog with a regular expresion as the dialog 
title e.g.
  FindDialog "^Explorer" 
  #(the ^ is to make sure you don't match the Command prompt window you are in!)
  
But you could use other regular expressions also e.g. - the first windows 
with 'Document' in the title,
".*[D]ocument.*"  (again the [ and ] are to make sure that the current 
command prompt window is not found!)

Note that this file needs Python24.dll - so if you have moved it out - this 
program will not work!.