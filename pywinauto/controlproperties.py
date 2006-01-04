# Control Properties
from win32structures import RECT, LOGFONTW

from pprint import pprint

#====================================================================
class ControlProps(dict):
	#----------------------------------------------------------------
	def __init__(self, props = {}):
		# default to having menuItems for all things
		self.MenuItems = []
		
		self.update(props)
		#for x in props:
			#self[x] = props[x]
			
		if hasattr(props, "handle"):
			self.__dict__['handle'] = props.handle
		else:
			self.__dict__['handle'] = None
		
		self.__dict__['ref'] = None
	
	#----------------------------------------------------------------
	# handles attribute access for dictionary items and
	# for plurals (e.g. if self.Fonts = [4, 2] then self.Font = 4)
	def __getattr__(self, key):
		
		# if the key is not in the dictionary but the plural is
		if key not in self and key + "s" in self:
		
			# try to get the first element of the possible list item
			try:
				return self[key + "s"][0] 
			except TypeError, e:
				pass
		
		if key in self:
			return self[key] 
		
		return self.__dict__[key]

	#----------------------------------------------------------------
	def __setattr__(self, key, value):
		if key in self.__dict__:
			self.__dict__[key] = value
		else:
			self[key] = value  
			
	#----------------------------------------------------------------
	def HasStyle(self, flag):
		return self.Style & flag == flag

	#----------------------------------------------------------------
	def HasExStyle(self, flag):
		return self.ExStyle & flag == flag
	
	
	


#====================================================================
def GetMenuBlocks(ctrls):
	allMenuBlocks = []
	for ctrl in ctrls:
		if ctrl.has_key('MenuItems'):

			# we need to get all the separate menu blocks!
			menuBlocks = MenuBlockAsControls(ctrl.MenuItems)
			allMenuBlocks.extend(menuBlocks)

	return allMenuBlocks


#====================================================================
def MenuBlockAsControls(menuItems, parentage = []):

	blocks = []

	curBlock = []
	for item in menuItems:

		# do a bit of conversion first :-)
		itemAsCtrl = MenuItemAsControl(item)

		# update the FriendlyClassName to contain the 'path' to 
		# this particular item
		itemPath = "%s->%s" % ("->".join(parentage), item['Text'])
		itemAsCtrl.FriendlyClassName = "MenuItem %s" %itemPath

		#append the item to the current menu block
		curBlock.append(itemAsCtrl)

		# If the item has a sub menu
		if item.has_key('MenuItems'):

			# add the current item the path
			parentage.append(item['Text'])

			# Get the block for the SubMenu, and add it to the list of
			# blocks we have found
			blocks.extend(MenuBlockAsControls(item['MenuItems'], parentage))
			
			# and seeing as we are dong with that sub menu remove the current
			# item from the path
			del(parentage[-1])

	# add the current block to the list of blocks
	blocks.append(curBlock)

	return blocks


#====================================================================
def MenuItemAsControl(menuItem):
	itemAsCtrl = ControlProps()

	itemAsCtrl["Texts"] = [menuItem['Text'], ]
	itemAsCtrl["ControlID"] = menuItem['ID']
	itemAsCtrl["Type"] = menuItem['Type']
	itemAsCtrl["State"] = menuItem['State']

	itemAsCtrl["Class"] = "MenuItem"
	itemAsCtrl["FriendlyClassName"] = "MenuItem"

	# as most of these don't matter - just set them up with default stuff
	itemAsCtrl["Rectangle"] = RECT(0, 0, 999, 999)
	itemAsCtrl["Fonts"] = [LOGFONTW(), ]
	itemAsCtrl["ClientRects"] = [RECT(0, 0, 999, 999), ]
	itemAsCtrl["ContextHelpID"] = 0
	itemAsCtrl["UserData"]  = 0
	itemAsCtrl["Style"] = 0
	itemAsCtrl["ExStyle"] = 0
	itemAsCtrl["IsVisible"] = 1

	return itemAsCtrl



#====================================================================
def SetReferenceControls(controls, refControls):

	# numbers of controls must be the same (though in future I could imagine
	# relaxing this constraint)
	
	if len(controls) != len(refControls):
		#print len(controls), len(refControls)
		#pprint(controls)
		#print "=="  * 20
		#pprint(refControls)
		raise "Numbers of controls on ref. dialog does not match Loc. dialog"

	# set the controls
	for i, ctrl in enumerate(controls):
		ctrl.ref = refControls[i]
	
	toRet = 1
	allIDsSameFlag = 2
	allClassesSameFlag = 4
	
	# find if all the control id's match
	if  [ctrl.ControlID for ctrl in controls] == \
		[ctrl.ControlID for ctrl in refControls]:
		
		toRet += allIDsSameFlag

	# check if the control classes match
	if [ctrl.Class for ctrl in controls] == \
	   [ctrl.Class for ctrl in refControls]:
	
		toRet += allClassesSameFlag
	
	return toRet


		
			