def serialise_cookies(value_set):
	output= "|".join("%s=%s" %(str(x),str(value_set[x])) for x in value_set)
	return output



def deserialise_cookies(cookie_string):
	user_settings = {}
	if cookie_string:
		cookie_set = cookie_string.split("|")
		for pair in cookie_set:
			key_value= pair.split("=")
			if not key_value[1]:
				key_value.pop()
				continue
				
			key, value = key_value
			user_settings[key] = value
	return user_settings




# some_dict ={"1":"abc", "2":"asd", "3":"sdg"}
#cookie_string = "chkDefaultCustDist=|rdioDefaultUnits=km"
# print serialise_cookies(some_dict)
#print deserialise_cookies(cookie_string)
