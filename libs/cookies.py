import hmac
import logging


def serialise_cookies(value_set):
	output= "%".join("%s=%s" %(str(x),str(value_set[x])) for x in value_set)
	return create_secure_cookie(output)



def deserialise_cookies(cookie_string):
	user_settings = {}
	if cookie_string:
		decrypted_cookie_set = decrypt_secure_cookie(cookie_string)
		if decrypted_cookie_set:
			decrypted_cookie_set = decrypted_cookie_set.split("%")
			for pair in decrypted_cookie_set:
				key_value= pair.split("=")
				if not key_value[1]:
					key_value.pop()
					continue
					
				key, value = key_value
				user_settings[key] = value
	return user_settings

secure = "yadda-yadda-badda"

def create_secure_cookie(cookie_value):
	hashed_cookie = hmac.new(secure, str(cookie_value)).hexdigest()
	return str("%s|%s" %(cookie_value, hashed_cookie))


def decrypt_secure_cookie(hashed_cookie):
	if hashed_cookie:
		value, cookie_hash = hashed_cookie.split("|")

		if value and hashed_cookie == create_secure_cookie(value):
			return str(value)
	else:
		return None

# some_dict ={"1":"abc", "2":"asd", "3":"sdg"}
#cookie_string = "chkDefaultCustDist=true%rdioLocalUnits=km|a956c665a3382564bc72e63ee8ea26bf"
# print serialise_cookies(some_dict)
#print deserialise_cookies(cookie_string)



# create_secure_cookie( "something")
#print decrypt_secure_cookie(cookie_string)

#print serialise_cookies({"chkDefaultCustDist":"true", "chk":"true"})