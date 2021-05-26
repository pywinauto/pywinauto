"""Build up the sphinx autodoc file for the python code"""
from __future__ import print_function

import os
import sys

docs_folder = os.path.dirname(__file__)
pywin_folder = os.path.dirname(docs_folder)

sys.path.append(pywin_folder)
pywin_folder = os.path.join(pywin_folder, "pywinauto")

excluded_dirs = ["unittests"]
excluded_files = [
    "_menux.py",
    "__init__.py",
    "win32defines.py",
    "win32structures.py",
    "win32functions.py"]

output_folder = os.path.join(docs_folder, "code")

try:
    os.mkdir(output_folder)
except Exception:
    pass

module_docs = []
for root, dirs, files in os.walk(pywin_folder):

    # Skip over directories we don't want to document
    for i, d in enumerate(dirs):
        if d in excluded_dirs:
            del dirs[i]

    py_files = [f for f in files if f.endswith(".py")]

    for py_filename in py_files:
        # skip over py files we don't want to document
        if py_filename in excluded_files:
            continue

        py_filepath =  os.path.join(root, py_filename)

        # find the last instance of 'pywinauto' to make a module name from
        # the path
        modulename = 'pywinauto' + py_filepath.rsplit("pywinauto", 1)[1]
        modulename = os.path.splitext(modulename)[0]
        modulename = modulename.replace(os.path.sep, '.')

        # the final doc name is the modulename + .txt
        doc_source_filename = os.path.join(output_folder, modulename + ".txt")

        # skip files that are already generated
        if os.path.exists(doc_source_filename):
            continue

        print(py_filename)

        with open(doc_source_filename, "w") as out:
            out.write(modulename + "\n")
            out.write("-" * len(modulename) + "\n")
            out.write(" .. automodule:: %s\n"% modulename)
            out.write("    :members:\n")
            out.write("    :undoc-members:\n\n")
            #out.write("    :inherited-members:\n")
            #out.write(" .. autoattribute:: %s\n"% modulename)

        module_docs.append(doc_source_filename)


# This section needs to be updated - I should ideally parse the
# existing file to see if any new docs have been added, if not then
# I should just leave the file alone rather than re-create.
#
#c = open(os.path.join(output_folder, "code.txt"), "w")
#c.write("Source Code\n")
#c.write("=" * 30 + "\n")
#
#c.write(".. toctree::\n")
#c.write("   :maxdepth: 3\n\n")
#for doc in module_docs:
#    c.write("   " + doc + "\n")
#
#c.close()
