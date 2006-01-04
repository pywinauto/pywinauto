import win32structures

def LeadTrailSpacesTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
		
		locLeadSpaces = GetLeadSpaces(win.Text)
		locTrailSpaces = GetTrailSpaces(win.Text)

		refLeadSpaces = GetLeadSpaces(win.ref.Text)
		refTrailSpaces = GetTrailSpaces(win.ref.Text)
		
		diffs = []
		if locLeadSpaces != refLeadSpaces:
			diffs.append("Leading", locLeadSpaces, locTrailSpaces)

		if locTrailSpaces != refTrailSpaces:
			diffs.append("Trailing", locTrailSpaces, refTrailSpaces)
		
		for diff, loc, ref in diffs:
			bugs.append((
				[win, ],
				{
					"Lead-Trail": diff,
					"Ref": ref,
					"Loc": loc,
				},
				"LeadTrailSpaces",
				0,)
			)
	return bugs


def GetLeadSpaces(title):
	spaces = ''
		
	for i in range(0, len(title)):
		if not title[i].isspace():
			break
		
		spaces += title[i]
		
	return spaces
		
		
def GetTrailSpaces(title):
	rev = "".join(reversed(title))
	spaces = GetLeadSpaces(rev)
	return "".join(reversed(spaces))


LeadTrailSpacesTest.TestsMenus = True	
