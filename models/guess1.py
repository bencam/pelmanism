#!/usr/bin/env python


"""
Add docstring

"""


from protorpc import messages
from google.appengine.ext import ndb


# Define guess1 object
class Guess1(ndb.Model):
    """Guess1 object; each Guess1 model is given a parent (game.key) in
    pelmansim_api.py; the Guess1 model is compared with the guess2 and
    guess2_int attributes in the make_move endpoint in pelmansim_api.py"""
    guess1 = ndb.StringProperty(required=True)
    guess1_int = ndb.IntegerProperty(required=True)
