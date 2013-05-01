import re

re_pace = re.compile(r"\d?\d:\d\d:\d\d{1}$|\d?\d:\d\d{1}$|\d\ds$")
def validate_input(pace):
	return pace and re_pace.match(pace)

#print validate_input("23:23")
