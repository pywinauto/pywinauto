
CharsToCheck = (
	">", 
	">>",
	"<", 
	"<<",
	"&",
	"&&",
	"...",
	":",
	"@",

)

#-----------------------------------------------------------------------------
def MissingExtraStringTest(windows):
	bugs = []
	for win in windows:
		if not win.ref:
			continue
	
		for char in CharsToCheck:
			missingExtra = ''
			
			if win.Text.count(char) > win.ref.Text.count(char):
				missingExtra = "ExtraCharacters"
			elif win.Text.count(char) < win.ref.Text.count(char):
				missingExtra = "MissingCharacters"
			
			if missingExtra:
				bugs.append((
					[win,],
					{
						"MissingOrExtra": missingExtra,
						"MissingOrExtraText": char 
					},
					"MissingExtraString",
					0))	
					
	return bugs


MissingExtraStringTest.TestsMenus = True
			
