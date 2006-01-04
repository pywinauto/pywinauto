#import set
from Test_RepeatedHotkey import GetHotkey

controls = (
	"&Hello",
	"&Exit",
	"&OK",
	"&Python",
	"&Ion Trail",
	"&Galaxy Quest",
	"&Xenon",
	"&Sierra",
	"&Zope",
	"&Sizzling",
	"Here &and Now",
	"&Later maybe",
	"&Scram",
	"Wo&w",
	"What is T&HAT",
	"&Mercury",
	"&Venus",
	"&Earth",
	"M&ercury",
	"Ven&us",
	"Ea&rth",
	"&Mercury",
	"&OK",
	"&Python",
	"&Ion Trail",
	"&Galaxy Quest",
	)


charIndex = {}
hotkeyCtrls = {}
allChars = set()
for ctrl in controls:
	# try to build up information on the dialog first
	# e.g. if it's possible to fix at all
	# any controls that have a unique character
	
	hotkeyCtrls.setdefault(GetHotkey(ctrl)[1].lower(), []).append(ctrl)
	allChars = allChars.union(set(ctrl.lower()))
	
	for c in ctrl:
		if c in ' _&': continue
		
		charIndex.setdefault(c.lower(), []).append(ctrl)


allChars.difference_update(" _&")

freeChars = allChars.difference(hotkeyCtrls.keys())
print freeChars


for c in hotkeyCtrls:
	print c
	for ctrl in hotkeyCtrls[c]:
		print "\t", ctrl

if len(allChars) < len(controls):
	print "impossible to fix completely because there are more hotkeys then individual characters in the dialog"
	print "the following characters are free:"
	
	#for c in freeChars:
	#	print "\t%s"% c
	#	for ctrl in charIndex[c]:
	#		print "\t\t%s" % ctrl
			
	usedChars = hotkeyCtrls.keys()
	
	changesMade = 1
	while changesMade:
		changesMade = 0
		
		for char, ctrls in charIndex.items():

			# if there is only one control that has this character
			if len (ctrls) == 1:
				# get the control
				ctrl = ctrls[0]
				
				# find the hotkey for that control
				ctrlHotkey = GetHotkey(ctrl)[1].lower()
				
				print ctrlHotkey, `ctrl`
				# remove the control from the list
				hotkeyCtrls[ctrlHotkey].remove(ctrl)
				
				# if there are now now controls for that hotkey
				# remove it
				if len(hotkeyCtrls[ctrlHotkey]) == 0:
					del(hotkeyCtrls[ctrlHotkey])
				
				# add the new changed one to the hotkeys
				hotkeyCtrls.setdefault(char, []).append(ctrl)
				changesMade = 1
else:
	

	for hotkey, ctrls in hotkeyCtrls.items():
		if len(ctrls) > 1:
			for ctrl in ctrls:
				ctrlChars = set(ctrl.lower()).difference(" &_")
				if freeChars.intersection(ctrlChars):
					
	


print "="*100

for c in hotkeyCtrls:
	print c
	for ctrl in hotkeyCtrls[c]:
		print "\t", ctrl

	
	

#for x in charIndex:
#	print x, charIndex[x]
	
for hotkey, ctrls in hotkeyCtrls.items():
	if len(ctrls) > 1:
		print "***** BUG *****"
		print "\t", hotkey, ctrls
		
		# find the chars free for each control
		ctrlFree = []
		for ctrl in ctrls:
			ctrlFree.append("".join(set(ctrl.lower()).intersection(freeChars)))
		
		# count the controls with no hotkey free
		countNotFree = len([c for c in ctrlFree if not c])
		if countNotFree > 1:
			print "Cannot be fixed without possibly changing other controls also"
		
		for i, free in enumerate(ctrlFree):
			if not free:
				print "Must leave '%s' alone" %ctrls[i]
		
		

	
	
	



import sys
sys.exit()

#================================================
#================================================
#================================================
#================================================
#================================================







	
# return the controls that have characters in common with
# the control
def GetCtrlsWithSameChars(ctrl, controls):
	ourChars = set(ctrl.lower())
	ourChars.difference_update("& _")
	
	toRet = []
	for control in controls:
		ctrlChars = set(control.lower())
	
		if ourChars.intersection(ctrlChars):
			toRet.append(control)
	
	return toRet


def GetFreeCharsForControls(allFree, controls):
	ctrlFree = []
	allCtrlsFree = []
	for ctrl in controls:
		curCtrlFree = set(ctrl.lower()).intersection(allFree)
		ctrlFree.append("".join(curCtrlFree))
		
		allCtrlsFree.extend(curCtrlFree)
	
	return ctrlFree, "".join(allCtrlsFree)
	
	
	
charIndex = {}
hotkeyCtrls = {}
for c in controls:
	hotkeyCtrls.setdefault(GetHotkey(c)[1].lower(), []).append(c)
	
	for char in c.lower():
		charIndex.setdefault(char, []).append(c)
	
	

hotkeys = set(hotkeyCtrls.keys())
allKeys = set("".join(controls).lower())
allKeys.difference_update("& _")

freeKeys = allKeys.difference(hotkeys)

print len(controls)
if len(controls) > len(allKeys):
	print "**** Oops - more hotkeys than available characters :-( "
	


	

	
for hotkey, ctrls in hotkeyCtrls.items():
	if len(ctrls) > 1:
		print "**bug**"
		
		# can it be fixed simply by changing one or more of the controls
		# to another character within these controls
		
		ctrlsFreeChars, allFree = GetFreeCharsForControls(freeKeys, ctrls)
		
		# find out if we can use this method (0 or 1 controls with no free characters)
		noFreeCount = 0
		for i, ctrl in enumerate(ctrls):
			if not ctrlsFreeChars[i]:
				noFreeCount += 1
		
		# ok - so more than one control has no free chars - can't use the 
		# simple method
		if noFreeCount > 1:
			print "cant use that method"
			continue
		
		if noFreeCount == 0:
			extraText = ' or leave the same'
		else:
			extraText = ''
		
		for i, ctrl in enumerate(ctrls):
			if len(ctrlsFreeChars[i]) > 1:
				print "Change '%s' to one of (%s)%s"% (ctrl, "".join(ctrlsFreeChars[i]), extraText)
			elif len(ctrlsFreeChars[i]) == 1:
				print "Change '%s' to %s%s"% (ctrl, "".join(ctrlsFreeChars[i]), extraText)
			else:
				print "do not change %s" % ctrl
		
		
#		
#		for curCtrl in ctrls:
#			# Get the letters that could be used
#			ctrlAvl = set(curCtrl.lower()).intersection(freeKeys)
#			
#			#changesNeeded = ''
#			
#			# if there are no free letters in that control
#			# try and find if any other control could have it's 
#			# hotkey changed to free up for ourself
#			if len(ctrlAvl) == 0:
#			
#				# get the controls that share some letters		
#				otherCtrls = GetCtrlsWithSameChars(c, controls)
#				
#				suggestedChanges = []
#				# check if any of the letters in those controls can be freed up
#				for otherCtrl in otherCtrls:
#					if GetHotkey(otherCtrl)[1].lower() == hotkey:
#					freeOther = set(otherCtrl.lower()).intersection(freeKeys)
#					
#					if freeOther:
#						print "To Fix %s Free %s in %s by changing to any of (%s)"%(curCtrl, GetHotkey(otherCtrl)[1], otherCtrl, "".join(freeOther))
#			
#			
#			
##				posChange = set(c.lower()).intersection(allKeys)
##				changesNeeded = "".join(posChange)
##				
##				for char in posChange:
##					# get the controls that have that character
##					otherCtrls = charIndex[char]
##					
#			else:
#				print "To fix %s change %s to any of (%s)"% (curCtrl, c, "".join(ctrlAvl))
#				
#				
			
		#print "bug", ctrls, "".join(freeKeys)

