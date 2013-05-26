import re

re_pace = re.compile(r"\d?\d:\d\d:\d\d{1}$|\d?\d:\d\d{1}$|\d\ds$")
def validate_input(pace):
	return pace and re_pace.match(pace)

#print validate_input("23:23:0000:00")

re_distance = re.compile(r'^\d+\.?\d*$')
def validate_float(distance):
	return distance and re_distance.match(distance)

re_weight = re.compile(r'^\d+\.?\d*$')
def validate_weight(weight):
	return not weight or re_distance.match(weight)


#print validate_weight("2.3")