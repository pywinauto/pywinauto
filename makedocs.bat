@echo off


REM docs\build_autodoc_files.py
sphinx-build -b html doc_src pywinauto\docs

REM c:\.temp\pudge\pudge\cli  --documents doc_source\index.rst,doc_source\controls_overview.rst,doc_source\howto.rst,doc_source\getting_started.rst,history.txt,license.txt,todo.txt --title pywinauto  -v  -d website  -m pywinauto.application,pywinauto.taskbar,pywinauto.clipboard,pywinauto.timings,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests   -t doc_source\template




REM These are the python modules
REM application.py
REM clipboard.py
REM findbestmatch.py
REM findwindows.py
REM handleprops.py
REM taskbar.py
REM win32defines.py
REM win32functions.py
REM win32structures.py
REM XMLHelpers.py

REM controls
REM tests




REM c:\.temp\pudge\pudge\cli --title pywinauto -v -m pywinauto --documents docs\index.rst,history.txt,license.txt,todo.txt,docs\howto.rst -d pudge_output_green_paste   -t \.temp\pudge\pudge\template\green_paste

