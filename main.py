#!/usr/bin/python

"""Add docstring"""


import logging
import webapp2
from google.appengine.api import mail, app_identity
from pelmanism_api import PelmanismApi
from models import User


# Cron job for sending out a reminder email
class SendReminderEmail(webapp2.RequestHandler):
	def get(self):
		"""Add docstring"""
		app_id = app_identity.get_application_id()
		users = User.query(User.email != None)
		for user in users:
			subject = 'This is a reminder!'
			body = 'Hello {}, try out Pelmanism. It\'s fun!'.format(
				user.name)
			# This will send test emails to all users
			mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
				user.email,
				subject,
				body)


# Task queue for updating average moves remaining
class UpdateAverageMovesRemaining(webapp2.RequestHandler):
	def post(self):
		"""Add docstring"""
		PelmanismApi._cache_average_attempts()
		self.response.set_status(204)


# Register routes that point to the handlers defined above
app = webapp2.WSGIApplication([
	('/crons/send_reminder', SendReminderEmail),
	('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
