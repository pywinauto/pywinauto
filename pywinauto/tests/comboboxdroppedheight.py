
def ComboBoxDroppedHeightTest(windows):
	bugs = []
	for win in windows:	
		if not win.ref:
			continue
	
		if win.Class != "ComboBox" or win.ref.Class != "ComboBox":
			continue

		if win.DroppedRect.height() != win.ref.DroppedRect.height():
			#print win.DroppedRect.height(), win.DroppedRect.height()
		
			bugs.append((
				[win, ],
				{},
				"ComboBoxDroppedHeight",
				0,)
			)

	return bugs

