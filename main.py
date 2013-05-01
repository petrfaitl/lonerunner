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
from libs.converters import converter
from libs.validation import validate_input


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

class Calculator(Handler):
	def get(self, selUnits = "Select Units"):
		self.render("calculator.html", selUnits=selUnits)


	def post(self):
		pace = self.request.get("txtPace")
		units = self.request.get("selUnits")
		
		params = dict(selUnits = units,)

		if not validate_input(pace):
			params["txtPace"]= pace
			params["error"] = "Enter valid time [hh:mm:ss or mm:ss]"
		elif units == "Select Units":
			params["error_units"] = "Select Units"
			params["txtPace"]= pace
		else:
			params["txtPace"]= pace
			params["output"], params["speed"], params["speed_miles"] = converter(pace,units)


		self.render("calculator.html", **params)







app = webapp2.WSGIApplication([
							('/main/', Handler),
							('/', Calculator)
							], debug=True)
