import zipfile
import sys

zip = zipfile.ZipFile(sys.argv[1], "r")
infos = zip.infolist()


sortedInfo = {}
for i in infos:
	sortedInfo[i.filename] =  i
	
for k in sorted(sortedInfo.keys()):
	print "%-50s "%k, sortedInfo[k].create_system, sortedInfo[k].create_version, sortedInfo[k].extract_version