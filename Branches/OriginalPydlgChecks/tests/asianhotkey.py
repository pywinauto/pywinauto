import re

from repeatedhotkey import ImplementsHotkey, GetHotkey

#asianHotkeyRE = re.compile ("\(&.\)((\t.*)|(\\t.*)|(\(.*\))|:|(\.\.\.)|>|<|(\n.*)\s)*$")

asianHotkeyRE = re.compile (r"""
	\(&.\)		# the hotkey
	(
		(\t.*)|		# tab, and then anything
		#(\\t.*)|	# escaped tab, and then anything
		(\(.*\)		# anything in brackets
	)|
	\s*|			# any whitespace
	:|				# colon
	(\.\.\.)|		# elipsis
	>|				# greater than sign
	<|				# less than sign
	(\n.*)			# newline, and then anything
	\s)*$""", re.VERBOSE)


#-----------------------------------------------------------------------------
def AsianHotkeyTest(windows):
	"Return the repeated hotkey errors"	

	bugs = []
	
	for win in windows:
		# skip it if it doesn't implement hotkey functionality
		if not ImplementsHotkey(win):
			continue
	
		if AsianHotkeyFormatIncorrect(win.Text):
		
			bugs.append((
				[win,],
				{},
				"AsianHotkeyFormat",
				0)
			)	


	return bugs
	
	
#-----------------------------------------------------------------------------
def AsianHotkeyFormatIncorrect(text):
	# get the hotkey
	pos, char = GetHotkey(text)

	# if it has a hotkey then check that it is correct Asian format
	if char:
		#print text, char
		found = asianHotkeyRE.search(text)
		if not found:
			return True
	

	return False
	
	


#
#
#void CAsianHotkeyFormatTest::operator()(ControlPair control)
#{
#
#	// get the 1st title
#	std::string title = control.loc->Titles()[0];
#
#	// get the hotkey position
#	size_t hotkeyPos = GetHotkeyPos(title);
#	if (hotkeyPos == -1)
#		return;
#
#	// if it uses this '&' as a hoktey
#	if (!GetHotkeyCtrlData(control.loc))
#		return;
#
#	// if we have the reference check to make sure that the SAME
#	// hotkey character is used!
#	if (control.ref) {
#		char refHotkey = Hotkey(control.ref->Titles()[0]);
#		char locHotkey = Hotkey(control.loc->Titles()[0]);
#
#		if (refHotkey != locHotkey)
#			m_Bugs.push_back(new CAsianHotkeyFormatBug(control, "AsianHotkeyDiffRef"));
#	}
#
#
#
#	// ignore strings like "&X:"
#	if (title.length() <= 3)
#		return;
#		
#	
#	// so if we have reached here:
#		// the control REALLY has a hotkey
#		// and the lenght of the control is greater than 3
#
#	if (hotkeyPos - 2  >= 0 &&	// at least 4th character ".(&..."
#		hotkeyPos + 1 <= title.length()-1 &&		// at most 2nd last character "...(&H)"
#		title[hotkeyPos-2] == '(' &&
#		title[hotkeyPos+1] == ')' &&
#		hotkeyPos +1 == title.find_last_not_of("\n\t :")
#	   )
#	{
#		// OK So we know now that the format "..(&X).." is correct and that it is the 
#		// last non space character in the title
#		; // SO NO BUG!
#	}
#	else /// HEY - a bug!
#	{
#		m_Bugs.push_back(new CAsianHotkeyFormatBug(control, "AsianHotkeyFormat"));
#
#	}
#
#
#
#}
#

AsianHotkeyTest.TestsMenus = True
