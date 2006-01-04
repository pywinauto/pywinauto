# pylint: disable-msg=W0611

"""info on truncation test"""


__revision__ = "0.0.1"


from win32defines import *
from win32functions import *
from ctypes import byref
from win32structures import RECT


#==============================================================================
def TruncationTest(windows):
	"Actually do the test"

	truncations = []
	
	# for each of the windows in the dialog
	for win in windows:

		truncIdxs, truncStrings = FindTruncations(win)
		
		isInRef = -1

		# if there were any truncations for this control
		if truncIdxs:
		
			# now that we know there was at least one truncation
			# check if the reference control has truncations
			if win.ref:
				isInRef = 0
				refTruncIdxs, refTruncStrings = FindTruncations(win.ref)

				if refTruncIdxs:
					isInRef = 1
		
		
		
			truncIdxs = ",".join([unicode(x) for x in truncIdxs])
			truncStrings = '"%s"' % ",".join([unicode(x) for x in truncStrings])
			truncations.append((
				[win,], 
				{
					"StringIndices": truncIdxs, 
					"Strings": truncStrings,
				}, 
				u"Truncation", 
				isInRef)
			)
			
	# return all the truncations
	return truncations

#==============================================================================
def FindTruncations(ctrl):

	truncIdxs = []
	truncStrings = []

	# for each of the titles this dialog
	for idx, (text, rect, font, flags) in enumerate(GetTruncationInfo(ctrl)):

		# skip if there is no text
		if not text:
			continue
			
		# get the minimum rectangle
		minRect = GetMinimumRect(text, font, rect, flags)			

		# if the min rectangle is bigger than the rectangle of the
		# object
		if minRect.right > rect.right or \
			minRect.bottom > rect.bottom:

			# append the index and the rectangle to list of bug items
			truncIdxs.append(idx)
			truncStrings.append(text)

	return truncIdxs, truncStrings



#==============================================================================
def GetMinimumRect(text, font, usableRect, drawFlags):
	isTruncated = False

	# try to create the font
	# create a Display DC (compatible to the screen)
	txtDC = CreateDC(u"DISPLAY", None, None, None )
	
	hFontGUI = CreateFontIndirect(byref(font))

	# Maybe we could not get the font or we got the system font
	if not hFontGUI:

		# So just get the default system font
		hFontGUI = GetStockObject(DEFAULT_GUI_FONT)

		# if we still don't have a font!
		# ----- ie, we're on an antiquated OS, like NT 3.51
		if not hFontGUI:

			# ----- On Asian platforms, ANSI font won't show.
			if GetSystemMetrics(SM_DBCSENABLED):
				# ----- was...(SYSTEM_FONT)
				hFontGUI = GetStockObject(SYSTEM_FONT) 
			else:
				# ----- was...(SYSTEM_FONT)
				hFontGUI = GetStockObject(ANSI_VAR_FONT)


	# put our font into the Device Context
	SelectObject (txtDC, hFontGUI)


	modifiedRect = RECT(usableRect)
	# Now write the text to our DC with our font to get the
	# rectangle that the text needs to fit in
	DrawText (txtDC, # The DC
		unicode(text),		# The Title of the control
		-1,			# -1 because sTitle is NULL terminated
		byref(modifiedRect),	# The Rectangle to be calculated to
		#truncCtrlData.drawTextFormat | 
		DT_CALCRECT | drawFlags)

	#elif modifiedRect.right == usableRect.right and \
	#	modifiedRect.bottom == usableRect.bottom:
	#	print "Oh so you thought you were perfect!!!"


	# Delete the font we created
	DeleteObject(hFontGUI)

	# delete the Display context that we created
	DeleteDC(txtDC)
	
	return modifiedRect
		



#==============================================================================
def ButtonTruncInfo(win):
	"Return truncation data for buttons"
	lineFormat = DT_SINGLELINE

	widthAdj = 0
	heightAdj = 0
	
	# get the last byte of the style
	buttonStyle = win.Style & 0xF
	
	if win.HasStyle(BS_MULTILINE):
		lineFormat = DT_WORDBREAK
			
	if buttonStyle == BS_PUSHBUTTON:
		heightAdj = 4
		widthAdj = 5
		
	elif win.HasStyle(BS_PUSHLIKE):
		widthAdj = 3
		heightAdj = 3 # 3
		if win.HasStyle(BS_MULTILINE):
			widthAdj = 9
			heightAdj = 2 # 3
		
	elif buttonStyle == BS_CHECKBOX or buttonStyle == BS_AUTOCHECKBOX:
		widthAdj = 18

	elif buttonStyle == BS_RADIOBUTTON or buttonStyle == BS_AUTORADIOBUTTON:
		widthAdj = 19

	elif buttonStyle == BS_GROUPBOX:
		heightAdj = 4
		widthAdj = 9
		lineFormat = DT_SINGLELINE

	if win.HasStyle(BS_BITMAP) or win.HasStyle(BS_ICON):
		heightAdj = -9000
		widthAdj = -9000
		lineFormat = DT_WORDBREAK
	
	newRect = win.ClientRects[0]
	newRect.right -=  widthAdj
	newRect.bottom -=  heightAdj
	
	return [(win.Text, newRect, win.Font, lineFormat), ]
	
#==============================================================================
def ComboBoxTruncInfo(win):
	"Return truncation data for comboboxes"
	# canot wrap and never had a hotkey
	lineFormat = DT_SINGLELINE | DT_NOPREFIX
	
	if win.HasStyle(CBS_DROPDOWN) or win.HasStyle(CBS_DROPDOWNLIST):
		widthAdj = 2#5
	else:
		widthAdj = 3
	
	truncData = []
	for title in win.Texts:
		newRect = win.ClientRects[0]
		newRect.right -= widthAdj
		truncData.append((title, newRect, win.Font, lineFormat))
		#print title, newRect, win.Font, lineFormat
	
	return truncData

#==============================================================================
def ComboLBoxTruncInfo(win):
	"Return truncation data for comboboxes"
	# canot wrap and never had a hotkey
	lineFormat = DT_SINGLELINE | DT_NOPREFIX
	
	truncData = []
	for title in win.Texts:
		newRect = win.ClientRects[0]
		newRect.right -= 5
		truncData.append((title, newRect, win.Font, lineFormat))
	
	return truncData
	
	
#==============================================================================
def ListBoxTruncInfo(win):
	"Return truncation data for listboxes"
	# canot wrap and never had a hotkey
	lineFormat = DT_SINGLELINE | DT_NOPREFIX	
	
	truncData = []
	for title in win.Texts:
		newRect = win.ClientRects[0]
		newRect.right -= 2
		newRect.bottom -= 1
		truncData.append((title, newRect, win.Font, lineFormat))
	
	return truncData


#==============================================================================
def StaticTruncInfo(win):
	"Return truncation data for static controls"
	lineFormat = DT_WORDBREAK
	
	if win.HasStyle(SS_CENTERIMAGE) or \
		win.HasStyle(SS_SIMPLE) or \
		win.HasStyle(SS_LEFTNOWORDWRAP):
		lineFormat = DT_SINGLELINE
	
	if win.HasStyle(SS_NOPREFIX):
		lineFormat |= DT_NOPREFIX
	
	return [(win.Text, win.ClientRects[0], win.Font, lineFormat), ]
	
#==============================================================================
def EditTruncInfo(win):
	"Return truncation data for static controls"
	lineFormat = DT_WORDBREAK | DT_NOPREFIX
	
	if not win.HasStyle(ES_MULTILINE):
		lineFormat |= DT_SINGLELINE

	return [(win.Text, win.ClientRects[0], win.Font, lineFormat), ]
		

#==============================================================================
def DialogTruncInfo(win):
	"Return truncation data for dialog type windows"
	# move it down more into range

	newRect = win.ClientRects[0]

	newRect.top += 5
	newRect.left += 5
	newRect.right -= 5


	if win.HasStyle(WS_THICKFRAME):
		newRect.top += 1
		newRect.left += 1
		newRect.right -= 1

	# if it has the system menu but is a small caption
	# then the only button it can have is the close button
	if win.HasStyle(WS_SYSMENU) and (win.HasExStyle(WS_EX_PALETTEWINDOW) or 
		win.HasExStyle(WS_EX_TOOLWINDOW)):
		newRect.right -= 15


	# all the rest only need to be considered if there is a system menu.
	elif win.HasStyle(WS_SYSMENU):
		buttons = []
		# account for the close button
		newRect.right -= 18
		buttons.append('close')

		# account for Icon if it is not disabled
		if not win.HasExStyle(WS_EX_DLGMODALFRAME):
			newRect.left += 19 # icon


		# account for context sensitive help if set
		if win.HasExStyle(WS_EX_CONTEXTHELP) and not ( \
			win.HasStyle(WS_MAXIMIZEBOX) and win.HasStyle(WS_MINIMIZEBOX)):

			newRect.right -= 17

			# there is a bigger gap if the minimize box is there
			if win.HasStyle(WS_MINIMIZEBOX) or win.HasStyle(WS_MAXIMIZEBOX) or \
				win.HasStyle(WS_GROUP):
				newRect.right -= 3

			buttons.append('help')


		# account for Maximize button (but skip if WS_GROUP is set
		if win.HasStyle(WS_MINIMIZEBOX) or win.HasStyle(WS_MAXIMIZEBOX) or \
			win.HasStyle(WS_GROUP):
			
			newRect.right -= 32
			buttons.append('min')
			buttons.append('max')

		if buttons:
			# space between first button and dialog edge
			diff = 5

			# space for each button
			diff += len(buttons) * 16

			# space between close and next button
			if len(buttons) > 1:
				diff += 2

			# extra space between help and min buttons
			if 'min' in buttons and 'help' in buttons:
				diff += 4

	return [(win.Text, newRect, win.Font, DT_SINGLELINE), ]


#==============================================================================
def StatusBarTruncInfo(win):
	truncInfo = WindowTruncInfo(win)
	for i, (title, rect, font, flag) in enumerate(truncInfo):
		
		rect.bottom -= win.VertBorderWidth
		if i == 0:
			rect.right -= win.HorizBorderWidth
		else:
			rect.right -= win.InterBorderWidth

	return truncInfo
	
#==============================================================================
def HeaderTruncInfo(win):
	truncInfo = WindowTruncInfo(win)

	for i, (title, rect, font, flag) in enumerate(truncInfo):
		
		rect.right -= 12

	return truncInfo





#==============================================================================
def WindowTruncInfo(win):
	matchedItems = []

	for i, title in enumerate(win.Texts):
		
		# Use the client rects for rectangles
		if i < len(win.ClientRects):
			rect = win.ClientRects[i]
		else:
			# until we run out then just use the first 'main' client rectangle
			rect = win.ClientRects[0]
					
		# if we have fewer fonts than titles
		if len(win.Fonts)-1 < i:
			font = win.Font
		else:
			font = win.Fonts[i]

		# add the item
		matchedItems.append((win.Texts[i], rect, font, DT_SINGLELINE))
	
	return matchedItems



#==============================================================================
TruncInfo = {
	"#32770" : DialogTruncInfo,
	"ComboBox" : ComboBoxTruncInfo,
	"ComboLBox" : ComboLBoxTruncInfo,
	"ListBox" : ListBoxTruncInfo,
	"Button" : ButtonTruncInfo,
	"Edit": EditTruncInfo,
	"Static" : StaticTruncInfo,

#	"msctls_statusbar32" : StatusBarTruncInfo,
#	"HSStatusBar" : StatusBarTruncInfo,
#	"SysHeader32" : HeaderTruncInfo,

#	"SysListView32" :  ListViewTruncInfo,
	#"SysTreeView32" :
}

#==============================================================================
def GetTruncationInfo(win):
	"helper function to hide non special windows"
	if win.Class in TruncInfo:
		return TruncInfo[win.Class](win)
	else:

		return WindowTruncInfo(win)



