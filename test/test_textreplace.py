import aguktools.textreplace


def test_clean_dc_line():
	replace_list = (
		('this', 'that'),
		('the', 'other')
		)


	replace_strings = [
		['i don\'t like this', 'i don\'t like that'],
		['i don\'t like the other', 'i don\'t like other ootherr'],
	]

	for start, end in replace_strings:
		assert aguktools.textreplace.multi_replace(start, replace_list) == end


