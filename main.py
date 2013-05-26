#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import datetime
from libs.converters import converter, paceunits
from libs.validation import validate_input, validate_float, validate_weight
from libs.cookies import serialise_cookies, deserialise_cookies, create_secure_cookie, decrypt_secure_cookie
import logging


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


	def set_cookie(self, cookie_key, value_set):
		expires = (datetime.datetime.now() + datetime.timedelta(weeks=52)).strftime('%a, %d %b %Y %H:%M:%S GMT')
		serial_cookies = serialise_cookies(value_set)
		self.response.headers.add_header("Set-Cookie", "%s=%s;  Path=/; Expires=%s" %(cookie_key, serial_cookies, expires)) #; Domain= lone-runner.appspot.com;
	
	def read_cookie(self, cookie_name):
		cookie_val = self.request.cookies.get(cookie_name)
		value_set = deserialise_cookies(cookie_val)
		return value_set
	
	def get_user_prefs(self):
		user_settings = {}
		user_settings = self.read_cookie("user_prefs") #change user_prefs > user_settings
		# user_settings = dict.fromkeys(user_prefs, 'checked="checked"') #convering true values to checked boxes
		return user_settings

	def set_session_cookie(self, key, value):
		cookie_hash = create_secure_cookie(value)
		self.response.headers.add_header("Set-Cookie", "%s = %s; " %(key, cookie_hash) ) #Domain= lone-runner.appspot.com;

	def read_session_cookie(self, cookie_name):
		cookie_hash = self.request.cookies.get(cookie_name)
		return decrypt_secure_cookie(cookie_hash)


	#def initialize(self, *a, **kw):
	# 	webapp2.RequestHandler.initialize(self, *a, **kw)
		

class MainPage(Handler):
	def get(self):
		self.redirect("/pace-calculator")		

class Calculator(Handler):
	def get(self, selUnits = "Select Units"):
		user_settings = self.get_user_prefs()
		self.render("calculator.html", selUnits=selUnits, **user_settings )


	def post(self):
		pace = self.request.get("txtPace")
		units = self.request.get("selUnits")
		cust_flip = self.request.get("flip-custom")
		cust_distance = self.request.get("txtCustDistance")
		cust_units = self.request.get("customUnits")
		user_settings = self.get_user_prefs()

		params = dict(selUnits = str(units))
		if cust_flip == "on":
			units = cust_units
			
			if validate_float(cust_distance):
				distance = cust_distance
				params["distance"] = distance
				params["selUnits"] = str(distance+units)
			
			params["txtCustDistance"] = cust_distance
		else:
			distance = None
			#params["txtCustDistance"] = units
		weight = user_settings.get("txtWeight")
		logging.error("weight is: %s" %weight)
		

		if not validate_input(pace):
			params["txtPace"]= pace
			params["error"] = "Enter valid time [hh:mm:ss or mm:ss]"
		elif not units:
			params["error_units"] = "Select units"
			params["txtPace"]= pace
		elif cust_flip=="on" and not distance:
			params["error_units"] = "Enter valid distance"
			params["txtPace"]= pace
		else:
			params["cust_units"] = cust_units
			params["txtPace"]= pace
			params["paceunits"] = paceunits(str(pace))
			params["output"], params["speed"], params["speed_miles"], params["calories"] = converter(pace,distance,units, weight)
			

		
		params.update(user_settings)
		self.render("calculator.html",  **params) #**user_settings

class FAQ(Handler):
	def get(self):
		self.render("units-and-distances.html")

class Credits(Handler):
	def get(self):
		self.render("credits.html")


class Share(Handler):
	def get(self):
		self.render("share.html")

class Settings(Handler):

	def get(self):
		referer = self.request.referer
		self.set_session_cookie("referrer", referer)

		user_settings= self.get_user_prefs()
		
		self.render("settings.html", **user_settings)


	def post(self):
		has_error = None
		params = {}
		user_prefs = {}
		rdioDefaultUnits_value = self.request.get("rdioDefaultUnits")
		chkDefaultCustDist = self.request.get("chkDefaultCustDist")
		txtWeight = self.request.get("txtWeight")
		rdioDefaultGender = self.request.get("rdioDefaultGender")

		if rdioDefaultUnits_value:
			user_prefs["rdioDefaultUnits_%s" %rdioDefaultUnits_value]= "true" 

		
		if chkDefaultCustDist:
			user_prefs["chkDefaultCustDist"] = "true"

		
		if validate_weight(txtWeight):
			user_prefs["txtWeight"] = txtWeight
			rdioDefaultWeight = self.request.get("rdioDefaultWeight")
			user_prefs["rdioDefaultWeight"] = rdioDefaultWeight 
		else:
			params["error_weight"] = "Enter valid weight"
			has_error = True

		user_prefs["rdioDefaultGender_%s" %rdioDefaultGender] = "true"


		self.set_cookie("user_prefs",user_prefs)
		user_settings = self.get_user_prefs()
		
		referer = self.read_session_cookie("referrer")
		

		#self.render("settings.html",  **user_settings)
		if has_error:
			self.render("settings.html", **params)
		elif referer:
			self.redirect("/")
		else:
			self.redirect(referer)
		









app = webapp2.WSGIApplication([
							('/', MainPage),
							('/units-and-distances/?', FAQ),
							('/pace-calculator/?', Calculator),
							('/credits/?', Credits),
							('/share/?', Share),
							('/settings/?', Settings)
							], debug=True)
