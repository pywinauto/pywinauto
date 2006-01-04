import win32structures

def CompareToRefFontTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
		
		diffs = {}
		
		for f in win32structures.LOGFONTW._fields_:
			
			loc = getattr(win.Font, f[0])
			ref = getattr(win.ref.Font, f[0])
			if loc != ref:
				diffs.append(f[0], loc, ref)
			
		for diff, locVal, refVal in diffs.items():
			bugs.append((
				[win, ],
				{
					"ValueType": diff,
					"Ref": unicode(refVal),
					"Loc": unicode(locVal),
				},
				"CompareToRefFont",
				0,)
			)
	return bugs

