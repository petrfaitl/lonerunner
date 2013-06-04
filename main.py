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
import os, os.path
import webapp2
import jinja2
import datetime, time
from libs.converters import converter, paceunits
from libs.validation import validate_input, validate_float, validate_weight, validate_name, validate_email
from libs.cookies import serialise_cookies, deserialise_cookies, create_secure_cookie, decrypt_secure_cookie
import logging
from urlparse import urlparse
from google.appengine.api import mail


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
		self.response.headers.add_header("Set-Cookie", "%s=%s; Domain= lonerunner.info; Path=/; Expires=%s" %(cookie_key, serial_cookies, expires)) #; Domain= lonerunner.info;
	
	def read_cookie(self, cookie_name):
		cookie_val = self.request.cookies.get(cookie_name)
		value_set = deserialise_cookies(cookie_val)
		return value_set
	
	def get_user_prefs(self, cookie_name):
		user_settings = self.read_cookie(cookie_name)
		
		if not user_settings and self.request.cookies.get(cookie_name): #checking for cookie tampering
			self.response.delete_cookie(cookie_name) 
		return user_settings



	def set_session_cookie(self, key, value):
		cookie_hash = create_secure_cookie(value)
		self.response.headers.add_header("Set-Cookie", "%s = %s; Domain= lonerunner.info; " %(key, cookie_hash) ) #Domain= lonerunner.info;

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
		user_settings = self.get_user_prefs("user_prefs")
		local_prefs = self.get_user_prefs("local_prefs")
		user_settings.update(local_prefs)
		self.render("calculator.html", selUnits=selUnits, **user_settings )


	def post(self):
		pace = self.request.get("txtPace")
		units = self.request.get("selUnits")
		cust_flip = self.request.get("flip-custom")
		cust_distance = self.request.get("txtCustDistance")
		cust_units = self.request.get("customUnits")
		user_settings = self.get_user_prefs("user_prefs")
		
		local_prefs = dict(rdioLocalUnits = cust_units)
		params = dict(selUnits = str(units))
		distance = None
		if cust_flip == "on":
			units = cust_units
			
			if validate_float(cust_distance):
				distance = cust_distance
				params["distance"] = distance
				params["selUnits"] = str(distance+units)
			
			params["txtCustDistance"] = cust_distance
		else:
			pass
			# distance = None
			#params["txtCustDistance"] = units
		weight = user_settings.get("txtWeight")
		weight_units = user_settings.get("rdioDefaultWeight")
		

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
			params["output"], params["speed"], params["speed_miles"], params["calories"] = converter(pace,distance,units, weight, weight_units)
		
		if cust_flip:
			local_prefs["chkDefaultCustDist"] = "true"
		else:
			local_prefs["chkDefaultCustDist"] = "None"

		


		self.set_cookie("local_prefs",local_prefs)
		if not local_prefs:
			local_prefs = self.get_user_prefs("local_prefs")
			
		
		params.update(user_settings)
		params.update(local_prefs)
		self.render("calculator.html",  **params) 

class FAQ(Handler):
	def get(self):
		self.render("units-and-distances.html")

class Credits(Handler):
	def get(self):
		self.render("credits.html")


class Share(Handler):
	def get(self):
		self.render("share.html")

	def post(self):
		has_error = False
		sender_name = self.request.get("txtSenderName")
		sender_email = self.request.get("txtSenderEmail")
		recipient_name = self.request.get("txtRecipientName")
		recipient_email = self.request.get("txtRecipientEmail")
		email_content = self.request.get("selCannedResponse")
		cust_email_content = self.request.get("txtareaCustMessage")

		if email_content == "Custom":
			email_content = cust_email_content

		params = dict(txtSenderName=sender_name, txtSenderEmail=sender_email, txtRecipientName=recipient_name, txtRecipientEmail=recipient_email, txtareaCustMessage=email_content )
		

		if not validate_name(sender_name):
			has_error = True
			params["error_sender_name"] = "There is something not just right"
		elif not validate_email(sender_email):
			has_error = True
			params["error_sender_email"] = "There is something not just right"
		elif not validate_name(recipient_name):
			has_error = True
			params["error_recipient_name"] = "There is something not just right"
		elif not validate_email(recipient_email):
			has_error = True
			params["error_recipient_email"]	= "There is something not just right"		
		
		if not email_content:
			has_error = True
			params["error_textarea"] = "Surely, you'd like to say something. Try again."


		
		logging.error(params)

		message = mail.EmailMessage(sender="LoneRunner Pace Calculator <petr.faitl@lonerunner.info>",
                            subject="Your friend %s thought you might like this app" %sender_name)

		message.to = "%s <%s>" %(recipient_name, recipient_email)
		message.body = """
Hi %s,

%s

LoneRunner a running calculator and pace converter app.
Visit at http://www.lonerunner.info/


Regards,
%s


Sent from LoneRunner Pace Calculator webapp. You have received this email as somebody, you might know, thought you'd find it useful.
If you think this is spam or error, please send email to spam@lonerunner.info . 
""" %(recipient_name, email_content, sender_name)

		

		if has_error:
			self.render("share.html", error = has_error, **params)
		else:
			message.send()
			self.render("share.html", txtRecipientName = recipient_name, page_confirm = True)


class Settings(Handler):

	def get(self):
		referer = self.request.referer
		my_site = urlparse(self.request.url).netloc
		
		
		if referer and my_site in referer:
			self.set_session_cookie("referrer", referer)

		user_settings= self.get_user_prefs("user_prefs")
		
		self.render("settings.html", **user_settings)


	def post(self):
		has_error = None
		params = {}
		user_prefs = {}
		rdioDefaultUnits_value = self.request.get("rdioDefaultUnits")
		chkDefaultCustDist = self.request.get("chkDefaultCustDist")
		txtWeight = self.request.get("txtWeight")
		rdioDefaultGender = self.request.get("rdioDefaultGender")
		rdioDefaultWeight = self.request.get("rdioDefaultWeight")

		if rdioDefaultUnits_value:
			user_prefs["rdioDefaultUnits_%s" %rdioDefaultUnits_value]= "true" 

		
		if chkDefaultCustDist:
			user_prefs["chkDefaultCustDist"] = "true"

		
		if validate_weight(txtWeight,rdioDefaultWeight):
			user_prefs["txtWeight"] = txtWeight
			user_prefs["rdioDefaultWeight"] = rdioDefaultWeight 
		else:
			params["error_weight"] = "That doesn't look right"
			params["txtWeight"] = txtWeight
			has_error = True

		user_prefs["rdioDefaultGender_%s" %rdioDefaultGender] = "true"


		self.set_cookie("user_prefs",user_prefs)
		user_settings = self.get_user_prefs("user_prefs")
		referer = self.read_session_cookie("referrer")
		

		
		if has_error:
			self.render("settings.html", **params)
		elif not referer:
			self.redirect("/")
		else:
			self.redirect(referer)
		


class About(Handler):
	def get(self):
		build =  "Build: %s" % time.ctime(os.path.getmtime("main.py"))
		self.render("about.html", build_no = build)

class Feedback(Handler):
	def get(self):
		self.render("feedback.html")






app = webapp2.WSGIApplication([
							('/', MainPage),
							('/units-and-distances/?', FAQ),
							('/pace-calculator/?', Calculator),
							('/credits/?', Credits),
							('/share/?', Share),
							('/settings/?', Settings),
							('/about/?', About),
							('/feedback/?', Feedback),
							], debug=True)
