@echo off

python docs\build_autodoc_files.py

sphinx-build -w warnings.txt -E -b html .\docs .\html_docs 1>sphinx_build_log.txt 2>&1
::sphinx-build -w warnings.txt -E -b latex .\docs .\pdf_docs 1>sphinx_build_log.txt 2>&1
