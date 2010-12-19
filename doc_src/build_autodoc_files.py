"Build up the sphinx autodoc file for the python code"

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
except WindowsError:
    pass

module_docs = []
for root, dirs, files in os.walk(pywin_folder):

    # Skip over directories we don't want to document
    for i, d in enumerate(dirs):
        if d in excluded_dirs:
            del dirs[i]

    py_files = [f for f in files if f.endswith(".py")]
    
    for filename in py_files:
        # skip over py files we don't want to document
        if filename in excluded_files:
            continue
        
        # skip files that are already generated
        doc_source_filename = os.path.join(
            output_folder, filename + ".txt")
        if os.path.exists(doc_source_filename):
            continue
        
        print filename
        
        filepath =  os.path.join(root, filename)
                
        # find the last instance of 'pywinauto' to make a module name from
        # the path
        modulename = 'pywinauto' + filepath.rsplit("pywinauto", 1)[1]
        modulename = os.path.splitext(modulename)[0]
        modulename = modulename.replace('\\', '.')
        

        
        out = open(doc_source_filename, "w")
        
        out.write(modulename + "\n")
        out.write("-" * len(modulename) + "\n")
        out.write(" .. automodule:: %s\n"% modulename)
        out.write("    :members:\n")
        out.write("    :undoc-members:\n\n")
        #out.write("    :inherited-members:\n")
        #out.write(" .. autoattribute:: %s\n"% modulename)
        out.close()
        
        module_docs.append(doc_source_filename)


# This section needs to be updated - I should idealy parse the 
# existing file to see if any new docs have been added, if not then
# I should just leave the file alone rathre than re-create.
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
#        