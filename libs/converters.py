import re
import datetime

def converToTime(time_in_sec):
	return str(datetime.timedelta(seconds=time_in_sec))


def convertToSec(pace):
	time = re.findall(r'[0-9]+', pace)
	if len(time)<3:
		while len(time)<3:
			time.insert(0,"00")
	time_in_sec = 3600 * int(time[0]) + 60 * int(time[1]) + int(time[2]) 
	return time_in_sec



def converter(pace, units):
	time_in_sec =  convertToSec(pace)

	mileage= {"min/mile":1.60934, "1200m":1.2 , "min/km":1.0, "800m":0.8, "400m":0.4, "1500m":1.5,"1600m":1.6, "5k":5.0, "10k":10.0, "Half":21.0975, "Marathon":42.195, "1000m":1.0, "1mile":1.60934 }

	
	pace_per_k= time_in_sec /mileage[units]
	speed =   round((mileage[units])/(time_in_sec) *3600,1)
	speed_miles = round(speed /1.60934,1)

	output = {}
	output["400m"] =[400,converToTime(int(pace_per_k * mileage["400m"]))]
	output["1000m"] = [1000,converToTime(int(pace_per_k * mileage["1000m"]))]
	output["800m"] = [800,converToTime(int(pace_per_k * mileage["800m"]))]
	output["1200m"] = [1200,converToTime(int(pace_per_k * mileage["1200m"]))]
	output["1500m"] = [1500,converToTime(int(pace_per_k * mileage["1500m"]))]
	output["1600m"] = [1600,converToTime(int(pace_per_k * mileage["1600m"]))]
	output["1mile"] = [1609,converToTime(int(pace_per_k * mileage["1mile"]))]
	output["5k"] = [5000,converToTime(int(pace_per_k * mileage["5k"]))]
	output["10k"] = [10000,converToTime(int(pace_per_k * mileage["10k"]))]
	output["Half"] = [26000,converToTime(int(pace_per_k * mileage["Half"]))]
	output["Marathon"] = [42000,converToTime(int(pace_per_k * mileage["Marathon"]))]
	



	return output, speed, speed_miles





#print converter("3:45", "min/km")