import re
import datetime
import time
import logging

def converToTime(time_in_sec):
	time = datetime.timedelta(seconds=round(time_in_sec,0))
	return str(time)


def convertToSec(pace):
	time = re.findall(r'[0-9]+', pace)
	if len(time)<3:
		while len(time)<3:
			time.insert(0,"00")
	time_in_sec = 3600 * int(time[0]) + 60 * int(time[1]) + int(time[2]) 
	return time_in_sec



def converter(pace, distance , units, weight, weight_units):
	time_in_sec =  convertToSec(pace)
	mileage= {"min/mile":1.60934, "1200m":1.2 , "min/km":1.0, "800m":0.8, "400m":0.4, "1500m":1.5,"1600m":1.6, "5k":5.0, "10k":10.0, "Half":21.0975, "Marathon":42.195, "1km":1.0, "1mile":1.60934 }
	kilometers = mileage.get(units)
	
	if distance or units not in mileage:
		if not distance:
			distance = re.findall(r'\d+\.?\d*', str(units))
			distance = distance[0]
			units = re.findall(r'[a-z]+', str(units))
			units = units[0]
			
		if "km" in units :
			mileage[str(distance+units)]= float(distance)/mileage["1km"]
		else:
			mileage[str(distance+units)] = float(distance)*mileage["1mile"]

		units= str(distance+units)
		kilometers = mileage.get(units)
	
	pace_per_k= time_in_sec /mileage[units]
	speed =   round((mileage[units])/(time_in_sec) *3600,1)
	speed_miles = round(speed /1.60934,1)
	if weight and kilometers:
		if weight_units == "lb":
			weightInKg = float(weight) * 0.453592
		elif weight_units == "st":
			weightInKg = float(weight) * 6.35029
		else:
			weightInKg = float(weight)

		calories = int(weightInKg * kilometers * 1.036)
	else:
		calories = "-"

	output = {}

	for distanceIter in mileage:
		if distanceIter == "min/km" or distanceIter == "min/mile":
			continue
		elif distance and distanceIter == units: 
			continue

		else:
			output[distanceIter] = [mileage[distanceIter], converToTime(float(pace_per_k * mileage[distanceIter]))]
	return output, speed, speed_miles, calories


def paceunits(pace):
	if "s" in pace:
		result= "ec"
	elif len(pace)>5:
		result = "hrs"
	else:
		result = "mins"
	return result



#print converter("8:00", "1", "miles")

#print paceunits("00:0")