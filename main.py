#!/usr/bin/env python


"""
The main.py file contains two handlers: SendReminderEmail
and UpdateAverageMovesRemaining.

SendReminderEmail sends a reminder email every 24 hours to all
registered users who have at least one active game. The handler
is called by a cron job (see cron.yaml).

UpdateAverageMovesRemaining simply updates the average moves
remaining for all active games. The handler is called by a
taskqueue (see the get_average_attempts_remaining endpoint in
pelmanism_api.py).

"""


import logging
import webapp2
from google.appengine.api import mail, app_identity
from pelmanism_api import PelmanismApi
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):

    def get(self):
        """Send a reminder email to all users with at least one active game;
        call the handler every 24 hours using a cron job"""
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        msg = ('\n\nIt looks like you started a Pelmanism game, '
               'but haven\'t finished. Come back and find some matches!')
        for user in users:
            games = Game.query(Game.user == user.key).fetch()
            for game in games:
                if not game.game_over and not game.cancelled:
                    subject = 'Where did you go?'
                    body = 'Hi, {}!'.format(user.name) + msg
                    # This will send test emails to all users
                    mail.send_mail(
                        'noreply@{}.appspotmail.com'.format(app_id),
                        user.email,
                        subject,
                        body)
                    break


class UpdateAverageMovesRemaining(webapp2.RequestHandler):

    def post(self):
        """Update average moves remaining"""
        PelmanismApi._cache_average_attempts()
        self.response.set_status(204)


# Register routes that point to the handlers defined above
app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/cache_average_attempts', UpdateAverageMovesRemaining),
], debug=True)
