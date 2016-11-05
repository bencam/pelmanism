#!/usr/bin/python

"""Add docstring"""


import logging
import webapp2
from google.appengine.api import mail, app_identity
from pelmanism_api import PelmanismApi
from models import User, Game


# Cron job for sending out a reminder email
class SendReminderEmail(webapp2.RequestHandler):
	def get(self):
		"""Add docstring"""
		app_id = app_identity.get_application_id()
		users = User.query(User.email != None)
		msg = ('\n\nIt looks like you started a Pelmanism game, '
			'but haven\'t finished. Come back and find some matches!')
		for user in users:
			games = Game.query(Game.user == user.key).fetch()
			for g in games:
				if g.game_over == False:
					if g.cancelled == False:
						subject = 'Where did you go?'
						body = 'Hi, {}!'.format(user.name) + msg
						# This will send test emails to all users
						mail.send_mail(
							'noreply@{}.appspotmail.com'.format(app_id),
							user.email,
							subject,
							body)
						break


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
