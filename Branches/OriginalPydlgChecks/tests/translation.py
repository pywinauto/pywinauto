import re

#-----------------------------------------------------------------------------
def TranslationTest(windows):
	"Returns just one bug for each control"

	bugs = []
	for win in windows:
		if not win.ref:
			continue
			
		# get if any items are untranslated
		untranTitles, untranIndices = GetUntranslations(win)
		
		if untranTitles:
			indicesAsString = ",".join([unicode(x) for x in untranIndices])
		
			bugs.append((
				[win,],
				{
					"StringIndices": indicesAsString,
					"Strings": ('"%s"' % '","'.join(untranTitles))
				},
				"Translation",
				0)
			)	


	return bugs

def GetUntranslations(win):
    # remove ampersands and other non translatable bits from the string

	nonTransChars = re.compile(
		"""(\&(?!\&)|	# ampersand not followed by an ampersand
			\.\.\.$|	# elipsis ...
			^\s*|		# leading whitespace
			\s*$|		# trailing whitespace
			\s*:\s*$	# trailing colon (with/without whitespace)
			)*			# repeated as often as necessary
			""", re.X)
	

	# clean each of the loc titles for comparison
	cleanedLocTitles = []
	for title in win.Texts:
		cleanedLocTitles.append(nonTransChars.sub("", title))

	# clean each of the ref titles for comparison
	cleanedRefTitles = []
	for title in win.ref.Texts:
		cleanedRefTitles.append(nonTransChars.sub("", title))

	untranslatedTitles = []
	untranslatedIndices = []
	
	# loop over each of the cleaned loc title
	for index, title in enumerate(cleanedLocTitles):
		
		# if the title is empty just skip it
		if not title:
			continue

		# if that title is in the cleaned Ref Titles
		if title in cleanedRefTitles:
			# add this as one of the bugs
			untranslatedTitles.append(title)
			untranslatedIndices.append(index)
			
	# return all the untranslated titles and thier indices
	return untranslatedTitles, untranslatedIndices


TranslationTest.TestsMenus = True
	
