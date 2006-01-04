import re

#-----------------------------------------------------------------------------
def AllControlsTest(windows):
	"Returns just one bug for each control"
	
	bugs = []
	for win in windows:
		bugs.append((
			[win,],
			{},
			"AllControls",
			0
		))	


	return bugs

