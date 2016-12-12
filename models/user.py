#!/usr/bin/env python


"""
Add docstring

"""


from datetime import datetime
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
