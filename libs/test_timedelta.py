import re
import datetime

#print re.findall(r'[0-9]+', '01:23:56')


def convertToSec(pace):
	time = re.findall(r'[0-9]+', pace)
	if len(time)<3:
		while len(time)<3:
			time.insert(0,"00")
	time_in_sec = 3660 * int(time[0]) + 60 * int(time[1]) + int(time[2]) 
	return time_in_sec



def converToTime(time_in_sec):
	return str(datetime.timedelta(seconds=time_in_sec))




print re.findall(r'\d+\.?\d*', "4")







#print converToTime(convertToSec("72"))