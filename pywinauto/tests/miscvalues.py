
def MiscValuesTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
		
		diffs = {}

		if win.Class != win.ref.Class:
			diffs["Class"] = (win.Class, win.ref.Class)

		
		if win.Style != win.ref.Style:
			diffs["Style"] = (win.Style, win.ref.Style())
			
		if win.ExStyle != win.ref.ExStyle:
			diffs["ExStyle"] = (win.ExStyle, win.ref.ExStyle)
		
		if win.ContextHelpID != win.ref.ContextHelpID:
			diffs["HelpID"] = (win.ContextHelpID, win.ref.ContextHelpID)
		
		if win.ControlID != win.ref.ControlID:
			diffs["ControlID"] = (win.ControlID, win.ref.ControlID)
			
		if win.IsVisible != win.ref.IsVisible:
			diffs["Visibility"] = (win.IsVisible, win.ref.IsVisible)
			
		if win.UserData != win.ref.UserData:
			diffs["UserData"] = (win.UserData, win.ref.UserData)
			
			
		for diff, vals in diffs.items():
			bugs.append((
				[win, ],
				{
					"ValueType": diff,
					"Ref": unicode(vals[1]),
					"Loc": unicode(vals[0]),
				},
				"MiscValues",
				0,)
			)
	return bugs

