import re

re_pace = re.compile(r"\d?\d:\d\d:\d\d{1}$|\d?\d:\d\d{1}$|\d\ds$")
def validate_input(pace):
	return pace and re_pace.match(pace)

#print validate_input("23:23:0000:00")

re_distance = re.compile(r'^\d+\.?\d*$')
def validate_float(distance):
	return distance and re_distance.match(distance)

re_weight = re.compile(r'^\d+\.?\d*$')
def validate_weight(weight, units ):
	if weight:
		if units == "kg":
			if float(weight) < 20 or float(weight) >200:
				return False
		elif units == "lb":
			if float(weight) < 40 or float(weight) >400:
				return False
		elif units == "st":
			if float(weight) < 3.5 or float(weight) >31.5:
				return False
	return not weight or re_weight.match(weight)


#print validate_weight("", "kg")