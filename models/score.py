#!/usr/bin/env python


"""
Add docstring

"""


from datetime import datetime
from protorpc import messages
from google.appengine.ext import ndb


# Define score object
class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    time_completed = ndb.StringProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    attempts_made = ndb.IntegerProperty(required=True)
    game_deck = ndb.StringProperty(repeated=True)
    matches_found = ndb.IntegerProperty(required=True)
    points = ndb.IntegerProperty(required=True)

    def to_form(self):
        """Return a ScoreForm representation of the score"""
        return ScoreForm(
            user_name=self.user.get().name,
            won=self.won,
            time_completed=self.time_completed,
            attempts_made=self.attempts_made,
            game_deck=self.game_deck,
            matches_found=self.matches_found,
            points=self.points)


# Message definitions
class ScoreForm(messages.Message):
    """Used for outbound score information for finished games"""
    user_name = messages.StringField(1, required=True)
    time_completed = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    attempts_made = messages.IntegerField(4, required=True)
    game_deck = messages.StringField(5, repeated=True)
    matches_found = messages.IntegerField(6, required=True, default=0)
    points = messages.IntegerField(7, required=True, default=0)

class ScoreForms(messages.Message):
    """Outbound container for a list of ScoreForm forms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)
