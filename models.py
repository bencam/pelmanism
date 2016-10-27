#!/usr/bin/env python

"""In models.py the class definitions for the Google Datastore entities
that pelmanism uses are defined.
Message classes are also included in this file."""


import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


# ------------------------Define game objects------------------------
class User(ndb.Model):
	"""User profile"""
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty()


class Game(ndb.Model):
	"""ADD in docstring"""
	# This is the actual game object
	deck = ndb.StringProperty(repeated=True)
	disp_deck = ndb.StringProperty(repeated=True)
	attempts_allowed = ndb.IntegerProperty(required=True)
	attempts_remaining = ndb.IntegerProperty(required=True, default=30)
	game_over = ndb.BooleanProperty(required=True, default=False)
	guesses_made = ndb.IntegerProperty(required=True)
	match_list = ndb.StringProperty(repeated=True)
	match_list_int = ndb.IntegerProperty(repeated=True)
	matches_found = ndb.IntegerProperty(required=True)
	move1_or_move2 = ndb.IntegerProperty()
	user = ndb.KeyProperty(required=True, kind='User')

	@classmethod
	def new_game(
		cls, user, attempts, deck, disp_deck, guesses_made,
		match_list, match_list_int, matches_found, move1_or_move2):
		"""ADD in docstring"""
		# This function is for creating a new game
		# Check to make sure the number of attempts is less than 76
		if attempts > 75:
			raise ValueError(
				'Number of attempts can be no more than 75!')
		# ADD IN: must be > 20 in bit above
		game = Game(
			user=user,
			deck=deck,
			attempts_allowed=attempts,
			attempts_remaining=attempts,
			disp_deck=disp_deck,
			guesses_made=guesses_made,
			match_list=match_list,
			match_list_int=match_list_int,
			matches_found=matches_found,
			move1_or_move2=move1_or_move2,
			game_over=False)
		# Here we store (or create, then store) the stuff in the db
		game.put()
		return game


	def to_form(self, message):
		"""ADD in docstring"""
		# This returns a GameForm representation of Game
		form = GameForm()
		form.urlsafe_key = self.key.urlsafe()
		form.user_name = self.user.get().name
		form.attempts_remaining = self.attempts_remaining
		form.game_over = self.game_over
		form.deck = self.deck  # TESTING
		form.disp_deck = self.disp_deck
		form.guesses_made = self.guesses_made
		form.match_list = self.match_list
		form.matches_found = self.matches_found
		form.message = message
		return form


	def to_form_user_games(self):
		return GameFormUserGames(
			urlsafe_key=self.key.urlsafe(),
			user_name=self.user.get().name,
			attempts_remaining=self.attempts_remaining,
			game_over=self.game_over,
			disp_deck=self.disp_deck,
			guesses_made=self.guesses_made,
			match_list=self.match_list,
			matches_found=self.matches_found)


	def end_game(self, won=False):
		"""End the game;
		if won is True, the player won;
		if won is False, the player lost)"""
		self.game_over = True
		self.put()
		# Add the game to the score board
		# I think this is where we actually instantiate a Score object
		# In other words, a score is only returned when a game ends
		score = Score(
			user=self.user,
			date=date.today(),
			won=won,
			guesses_made=self.guesses_made,
			game_deck=self.deck,
			matches_found=self.matches_found)
		score.put()


class Guess1(ndb.Model):
	"""Add in docstring"""
	guess1 = ndb.StringProperty(required=True)
	guess1_int = ndb.IntegerProperty(required=True)


class Score(ndb.Model):
	"""Add in docstring"""
	user = ndb.KeyProperty(required=True, kind='User')
	date = ndb.DateProperty(required=True)
	won = ndb.BooleanProperty(required=True)
	guesses_made = ndb.IntegerProperty(required=True)
	game_deck = ndb.StringProperty(repeated=True)
	matches_found = ndb.IntegerProperty(required=True)

	def to_form(self):
		# This returns a ScoreForm representation of Score
		return ScoreForm(
			user_name=self.user.get().name,
			won=self.won,
			date=str(self.date),
			guesses_made=self.guesses_made,
			game_deck=self.game_deck,
			matches_found=self.matches_found)
# -------------------------End game objects--------------------------


# ------------------------Message definitions------------------------
# Here we imply create messages (not Datastore entities)
class GameForm(messages.Message):
	"""Add in docstring"""
	# This is the form we send to the person making the request
	urlsafe_key = messages.StringField(1, required=True)
	attempts_remaining = messages.IntegerField(2, required=True)
	game_over = messages.BooleanField(3, required=True)
	message = messages.StringField(4, required=True)
	user_name = messages.StringField(5, required=True)
	disp_deck = messages.StringField(6, repeated=True)
	guesses_made = messages.IntegerField(7, required=True)
	match_list = messages.StringField(8, repeated=True)
	matches_found = messages.IntegerField(9, required=True)
	deck = messages.StringField(10, repeated=True)  # TESTING


class GameFormUserGames(messages.Message):
	"""Add in docstring"""
	urlsafe_key = messages.StringField(1, required=True)
	attempts_remaining = messages.IntegerField(2, required=True)
	game_over = messages.BooleanField(3, required=True)
	user_name = messages.StringField(4, required=True)
	disp_deck = messages.StringField(5, repeated=True)
	guesses_made = messages.IntegerField(6, required=True)
	match_list = messages.StringField(7, repeated=True)
	matches_found = messages.IntegerField(8, required=True)


class GameForms(messages.Message):
	"""Add docstring"""
	items = messages.MessageField(GameFormUserGames, 1, repeated=True)


class NewGameForm(messages.Message):
	"""Add in docstring"""
	# This is the form the person making the request fills out
	# when they want to create a new game
	user_name = messages.StringField(1, required=True)
	attempts = messages.IntegerField(2, default=5)


class MakeMoveForm(messages.Message):
	"""Add in docstring"""
	# This is the form the person making the request
	# fills out to make a move
	guess = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
	"""Add docstring"""
	# This is a form we send to the person making the request
	user_name = messages.StringField(1, required=True)
	date = messages.StringField(2, required=True)
	won = messages.BooleanField(3, required=True)
	guesses_made = messages.IntegerField(4, required=True)
	game_deck = messages.StringField(5, repeated=True)
	matches_found = messages.IntegerField(6, required=True, default=0)


class ScoreForms(messages.Message):
	"""Add docstring"""
	# We send this form to the person making the request
	# It gives a list of all of the score objects
	items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
	"""Add in docstring"""
	message = messages.StringField(1, required=True)
# ----------------------End message definitions----------------------
