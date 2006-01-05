# GUI Application automation and testing library
# Copyright (C) 2006 Mark Mc Mahon
#
# This library is free software; you can redistribute it and/or 
# modify it under the terms of the GNU Lesser General Public License 
# as published by the Free Software Foundation; either version 2.1 
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public 
# License along with this library; if not, write to the 
#    Free Software Foundation, Inc.,
#    59 Temple Place,
#    Suite 330, 
#    Boston, MA 02111-1307 USA 

import re
import difflib


# TODO: Refactor so that it does not require FriendlyClassName
#       It would need to get the list of titles to match against
#       from somewhere else.

#====================================================================
class MatchError(IndexError):
	def __init__(self, msg = '', items = [], tofind = ''):
		Exception.__init__(self, msg)
		
		self.items = items
		self.tofind = tofind
	
	def __str__(self):
		return "Could not find '%s' in '%s'"% (self.tofind, self.items)
		
#====================================================================
def clean_text(text):

	# remove anything after the first tab
	text_before_tab = re.sub(r"\t.*", "", text)
	
	# remove any whitespace or non alphanumeric characters
	return re.sub(r"[^\w ]|\s+", "", text_before_tab).lower()



	
#====================================================================
def build_unique_index_map(items):
	mapped_items = {}
	
	#counters = {}
	for i, text in enumerate(items):
		text = clean_text(text)
	
		# no duplicates so just store it without modification
		if text not in mapped_items:
			mapped_items[text] = i
			
		# else this item appears multiple times
		else:
			# find unique text
			unique_text = text
			counter = 2
			while unique_text in mapped_items:
				unique_text = text + str(counter)
				counter += 1
			
			mapped_items[unique_text] = i
			
			if not mapped_items.has_key(text + "0"):
				mapped_items[text + "0"] = mapped_items[text]
				mapped_items[text + "1"] = mapped_items[text]
				
	return mapped_items
			


#====================================================================
def find_best_match(search_text, item_texts, items):
	search_text = clean_text(search_text)
	
	# Clean each item, make it unique and map to 
	# to the item index
	item_index_map = build_unique_index_map(item_texts)
	
	# find the list of best matches
	matches = difflib.get_close_matches (search_text, item_index_map.keys())
	
	# best match is the first one - so get the index stored 
	# for that match text
	try:
		best_index = item_index_map[matches[0]]
	except IndexError:
		raise MatchError(items = item_texts, tofind = search_text)
	
	
	return items[best_index]
	
		
		
#====================================================================
def get_control_names(control):
	names = []
	
	# if it has a reference control - then use that
	if hasattr(control, 'ref') and control.ref:
		control = control.ref

	# Add the control based on it's friendly class name
	names.append(control.FriendlyClassName)
	
	# if it has some character text then add it base on that
	# and based on that with friendly class name appended
	if clean_text(control.Text): 
		names.append(control.Text)
		names.append(control.Text + control.FriendlyClassName)
	
	# return the names (either 1 or 3 strings)
	return names
	
	
#====================================================================
def junk_func(char):
	if char in ':"/ \t\n\r][{}=-\\|!@#$%^&*,.<>?/()':
		return True

	return False



#====================================================================
def clean_text2(text): # doesn't change text to lowercase

	# remove anything after the first tab
	text_before_tab = re.sub(r"\t.*", "", text)
	
	# remove any whitespace or non alphanumeric characters
	return re.sub(r"\W", "", text_before_tab)


#====================================================================
def find_best_control_match(search_text, controls):


	name_control_map = {}
	
	# collect all the possible names for all controls
	# and build a list of them
	for c in controls:
		ctrl_names = get_control_names(c)
		ctrl_names = [clean_text2(n) for n in ctrl_names]
		
		# remove duplicates
		ctrl_names = list(set(ctrl_names))
		
		# for each of the names
		for n in ctrl_names:

			# if its not there already then just add it			
			if not name_control_map.has_key(n):
			
				name_control_map[n] = c
	
			# else this item appears multiple times
			else:
				# find unique name
				unique_text = n
				counter = 2
				while unique_text in name_control_map:
					unique_text = n + str(counter)
					counter += 1

				# add it with that unique text
				name_control_map[unique_text] = c

				# and if this was the first time that we noticied that
				# it was a duplicated name then add new items based on the 
				# duplicated name but add '0' and '1' 
				if not name_control_map.has_key(n + "0"):
					name_control_map[n + "0"] = name_control_map[n]
					name_control_map[n + "1"] = name_control_map[n]
				
	
	# now time to figre out the matching
	ratio_calc = difflib.SequenceMatcher()	
	ratio_calc.set_seq1(clean_text2(search_text))

	best_ratio = 0
	best_control = None
	
	for name, control in name_control_map.items():
		ratio_calc.set_seq2(name)
		
		if ratio_calc.ratio() > best_ratio:
			best_ratio = ratio_calc.quick_ratio()
			best_control = control

	if best_ratio < .5:
		raise MatchError(items = name_control_map.keys(), tofind = search_text)
		
	return best_control
		
			
