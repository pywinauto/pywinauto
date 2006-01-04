from win32structures import RECT

#====================================================================
def MissalignmentTest(windows):

	refAlignments = {}

	#find the controls alligned along each axis
	for win in windows:
		if not win.ref:
			continue
	

		for side in ("top", "left", "right", "bottom"):
			sideValue = getattr(win.ref.Rectangle, side)
			
			# make sure that the side dictionary has been created
			sideAlignments = refAlignments.setdefault(side, {})
			
			# make sure that the array of controls for this
			# alignment line has been created and add the current window
			sideAlignments.setdefault(sideValue, []).append(win)
			
	bugs = []
	for side in refAlignments:
		for alignment in refAlignments[side]:
			controls = refAlignments[side][alignment]
			sides = [getattr(c.Rectangle, side) for c in controls]
			sides = set(sides)			
			
			if len(sides) > 1:

				overAllRect = RECT()
				overAllRect.left = min([c.Rectangle.left for c in controls])
				overAllRect.top = min([c.Rectangle.top for c in controls])
				overAllRect.right = max([c.Rectangle.right for c in controls])
				overAllRect.bottom = max([c.Rectangle.bottom for c in controls])

			
				bugs.append((
					controls, 
					{
						"AlignmentType": side.upper(),
						"AlignmentRect": overAllRect
					}, 
					"Missalignment", 
					0)
				)
				
	return bugs

