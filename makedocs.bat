@echo off

c:\.temp\pudge\pudge\cli --documents docs\about.rst,docs\index.rst,history.txt,license.txt,todo.txt --title pywinauto -v -d pudge_output_green_paste -m pywinauto.application,pywinauto.clipboard,pywinauto.controlactions,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests  -t \.temp\pudge\pudge\template\green_paste

REM --documents docs\about.rst

REM c:\.temp\pudge\pudge\cli --title pywinauto -v -d pudge_output_green -m pywinauto.application,pywinauto.clipboard,pywinauto.controlactions,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests  -t \.temp\pudge\pudge\template\green

REM c:\.temp\pudge\pudge\cli --title pywinauto -v -d pudge_output_lesscode -m pywinauto.application,pywinauto.clipboard,pywinauto.controlactions,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests  -t \.temp\pudge\pudge\template\lesscode.org
REM c:\.temp\pudge\pudge\cli --title pywinauto -v -d pudge_output_base -m pywinauto.application,pywinauto.clipboard,pywinauto.controlactions,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests  -t \.temp\pudge\pudge\template\base
REM c:\.temp\pudge\pudge\cli --title pywinauto -v -d pudge_output_pythonpaste -m pywinauto.application,pywinauto.clipboard,pywinauto.controlactions,pywinauto.findbestmatch,pywinauto.findwindows,pywinauto.handleprops,pywinauto.XMLHelpers,pywinauto.controls,pywinauto.tests  -t \.temp\pudge\pudge\template\pythonpaste.org

REM pywinauto.win32defines
REM pywinauto.win32functions
REM pywinauto.win32structures


REM pywinauto.application, pywinauto.clipboard, pywinauto.controlactions, pywinauto.findbestmatch, pywinauto.findwindows, pywinauto.handleprops, pywinauto.XMLHelpers, pywinauto.controls, pywinauto.tests