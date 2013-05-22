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
from libs.validation import validate_input
from libs.cookies import serialise_cookies, deserialise_cookies
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
		self.response.headers.add_header("Set-Cookie", "%s=%s; Domain= lone-runner.appspot.com; Path=/; Expires=%s" %(cookie_key, serial_cookies, expires)) #; Domain= lone-runner.appspot.com;
	
	def read_cookie(self, cookie_name):
		cookie_val = self.request.cookies.get(cookie_name)
		value_set = deserialise_cookies(cookie_val)
		return value_set
	
	def get_user_prefs(self):
		user_settings = {}
		user_settings = self.read_cookie("user_prefs") #change user_prefs > user_settings
		# user_settings = dict.fromkeys(user_prefs, 'checked="checked"') #convering true values to checked boxes
		return user_settings

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

		#logging.error("value of my cust_units is %s", str(cust_units))

		params = dict(selUnits = str(units))
		if cust_flip == "on":
			units = cust_units
			distance = cust_distance
			params["distance"] = distance
			params["selUnits"] = str(distance+units)
			params["txtCustDistance"] = cust_distance
		else:
			distance = None
			#params["txtCustDistance"] = units
		
		

		if not validate_input(pace):
			params["txtPace"]= pace
			params["error"] = "Enter valid time [hh:mm:ss or mm:ss]"
		elif not units:
			params["error_units"] = "Select Units"
			params["txtPace"]= pace
		elif cust_flip=="on" and not distance:
			params["error_units"] = "Select Units"
			params["txtPace"]= pace
		else:
			params["txtPace"]= pace
			params["paceunits"] = paceunits(str(pace))
			params["output"], params["speed"], params["speed_miles"] = converter(pace,distance,units)

		user_settings = self.get_user_prefs()
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

		user_settings= self.get_user_prefs()
		
		self.render("settings.html",  **user_settings)


	def post(self):
		user_prefs = {}
		rdioDefaultUnits_value = self.request.get("rdioDefaultUnits")
		if rdioDefaultUnits_value:
			user_prefs["rdioDefaultUnits_%s" %rdioDefaultUnits_value]= "true" 

		chkDefaultCustDist = self.request.get("chkDefaultCustDist")
		if chkDefaultCustDist:
			user_prefs["chkDefaultCustDist"] = "true"
		
		self.set_cookie("user_prefs",user_prefs)
		user_settings = self.get_user_prefs()
		
		#self.render("settings.html",  **user_settings)
		self.redirect("/")









app = webapp2.WSGIApplication([
							('/', MainPage),
							('/units-and-distances/?', FAQ),
							('/pace-calculator/?', Calculator),
							('/credits/?', Credits),
							('/share/?', Share),
							('/settings/?', Settings)
							], debug=True)
