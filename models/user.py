#!/usr/bin/env python


"""
Add docstring

"""


from protorpc import messages
from google.appengine.ext import ndb


# Define user object
class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    games_played = ndb.IntegerProperty(required=True)
    total_attempts = ndb.IntegerProperty(required=True)
    total_points = ndb.IntegerProperty(required=True)
    points_per_attempt = ndb.IntegerProperty(required=True)

    def to_rankings_form(self):
        """Return a UserRanking representation of the User"""
        return UserRanking(
            user_name=self.name,
            games_played=self.games_played,
            total_attempts=self.total_attempts,
            total_points=self.total_points,
            points_per_attempt=self.points_per_attempt)


# Message definitions
class UserRanking(messages.Message):
    """Used for outbound information regarding user rankings (players are
    ranked by points_per_attempt; total_points is used to break a tie)"""
    user_name = messages.StringField(1, required=True)
    games_played = messages.IntegerField(2, required=True)
    total_attempts = messages.IntegerField(3, required=True)
    total_points = messages.IntegerField(4, required=True)
    points_per_attempt = messages.IntegerField(5, required=True)

class UserRankings(messages.Message):
    """Outbound container for a list of UserRanking forms"""
    items = messages.MessageField(UserRanking, 1, repeated=True)

class StringMessage(messages.Message):
    """A single outbound string message"""
    message = messages.StringField(1, required=True)
