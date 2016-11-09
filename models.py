#!/usr/bin/env python

"""
The class definitions for the Google Datastore entities used by
Pelmanism are defined in models.py.

Pelmansim is made up of four models: User, Game, Guess1 and Score.

Message classes are also included in models.py. These are: GameForm,
GameFormUserGames, GameForms, NewGameForm, MakeMoveForm, ScoreForm,
ScoreForms, UserRanking, UserRankings, GameHistory and StringMessage.

"""


import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


# ------------------------Define game objects------------------------
class User(ndb.Model):
	"""User profile"""
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty()
	games_played = ndb.IntegerProperty(required=True)
	total_guesses = ndb.IntegerProperty(required=True)
	total_points = ndb.IntegerProperty(required=True)
	points_per_guess = ndb.IntegerProperty(required=True)

	def to_rankings_form(self):
		"""Return a UserRanking representation of the User"""
		return UserRanking(
			user_name=self.name,
			games_played=self.games_played,
			total_guesses=self.total_guesses,
			total_points=self.total_points,
			points_per_guess=self.points_per_guess)


class Game(ndb.Model):
	"""Game object"""
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
	cancelled = ndb.BooleanProperty(required=True, default=False)
	guess_history = ndb.StringProperty(repeated=True)
	user = ndb.KeyProperty(required=True, kind='User')

	@classmethod
	def new_game(cls, user, attempts, deck, disp_deck, guesses_made,
		match_list, match_list_int, matches_found, move1_or_move2,
		guess_history):
		"""Create and return a new game"""
		if attempts > 60:
			raise ValueError(
				'Number of attempts can be no more than 75!')
		# After TESTING, ADD IN: must be > 20 in bit above
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
			game_over=False,
			cancelled=False,
			guess_history=guess_history)
		game.put()
		return game

	def to_form(self, message):
		"""Return a GameForm representation of the game"""
		form = GameForm()
		form.urlsafe_key = self.key.urlsafe()
		form.user_name = self.user.get().name
		form.attempts_remaining = self.attempts_remaining
		form.game_over = self.game_over
		form.cancelled = self.cancelled
		form.deck = self.deck  # TESTING
		form.disp_deck = self.disp_deck
		form.guesses_made = self.guesses_made
		form.match_list = self.match_list
		form.matches_found = self.matches_found
		form.message = message
		return form

	def to_form_user_games(self):
		"""Return a GameFormUserGames representation of the game;
		this form displays a custom list of the game entities and is
		used in the get_user_games endpoint"""
		return GameFormUserGames(
			urlsafe_key=self.key.urlsafe(),
			user_name=self.user.get().name,
			attempts_remaining=self.attempts_remaining,
			game_over=self.game_over,
			disp_deck=self.disp_deck,
			guesses_made=self.guesses_made,
			match_list=self.match_list,
			matches_found=self.matches_found)

	def to_form_game_history(self, message):
		"""Return a GameHistory representation of the game;
		this form displays a custom list of the game entities and is
		used in the get_game_history endpoint"""
		return GameHistory(
			user_name=self.user.get().name,
			guess_history=self.guess_history,
			guesses_made=self.guesses_made,
			match_list=self.match_list,
			matches_found=self.matches_found,
			deck=self.deck,
			message=message)

	def end_game(self, won=False):
		"""End the game; if won is True, the player won;
		if won is False, the player lost"""
		self.game_over = True
		self.put()

		# Add the game to the score board
		# (a score is only returned when a game ends)
		points = self.points=(
			500 - ((self.guesses_made - self.matches_found) * 10))
		score = Score(
			user=self.user,
			date=date.today(),
			won=won,
			guesses_made=self.guesses_made,
			game_deck=self.deck,
			matches_found=self.matches_found,
			points=points)
		score.put()
		# TESTING LINES
		print ''
		print 'This is the score: %s' % score
		print ''
		# END TESTING LINES


class Guess1(ndb.Model):
	"""Guess1 object"""
	# The Guess1 model is used ... 
	guess1 = ndb.StringProperty(required=True)
	guess1_int = ndb.IntegerProperty(required=True)


class Score(ndb.Model):
	"""Score object"""
	user = ndb.KeyProperty(required=True, kind='User')
	date = ndb.DateProperty(required=True)
	won = ndb.BooleanProperty(required=True)
	guesses_made = ndb.IntegerProperty(required=True)
	game_deck = ndb.StringProperty(repeated=True)
	matches_found = ndb.IntegerProperty(required=True)
	points = ndb.IntegerProperty(required=True)

	def to_form(self):
		"""Return a ScoreForm representation of the score"""
		return ScoreForm(
			user_name=self.user.get().name,
			won=self.won,
			date=str(self.date),
			guesses_made=self.guesses_made,
			game_deck=self.game_deck,
			matches_found=self.matches_found,
			points=self.points)
# -------------------------End game objects--------------------------


# ------------------------Message definitions------------------------
class GameForm(messages.Message):
	"""Used for outbound game information"""
	urlsafe_key = messages.StringField(1, required=True)
	attempts_remaining = messages.IntegerField(2, required=True)
	game_over = messages.BooleanField(3, required=True)
	message = messages.StringField(4, required=True)
	user_name = messages.StringField(5, required=True)
	disp_deck = messages.StringField(6, repeated=True)
	guesses_made = messages.IntegerField(7, required=True)
	match_list = messages.StringField(8, repeated=True)
	matches_found = messages.IntegerField(9, required=True)
	cancelled = messages.BooleanField(10, required=True)
	deck = messages.StringField(11, repeated=True)  # TESTING


class GameFormUserGames(messages.Message):
	"""Used for outbound information on the state of a
	user's active games"""
	urlsafe_key = messages.StringField(1, required=True)
	attempts_remaining = messages.IntegerField(2, required=True)
	game_over = messages.BooleanField(3, required=True)
	user_name = messages.StringField(4, required=True)
	disp_deck = messages.StringField(5, repeated=True)
	guesses_made = messages.IntegerField(6, required=True)
	match_list = messages.StringField(7, repeated=True)
	matches_found = messages.IntegerField(8, required=True)


class GameForms(messages.Message):
	"""Return a list of GameFormUserGames"""
	items = messages.MessageField(GameFormUserGames, 1, repeated=True)


class NewGameForm(messages.Message):
	"""A form the user completes to create a new game"""
	user_name = messages.StringField(1, required=True)
	attempts = messages.IntegerField(2, default=5)


class MakeMoveForm(messages.Message):
	"""A form the user completes when making a move"""
	guess = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
	"""Used for outbound score information"""
	user_name = messages.StringField(1, required=True)
	date = messages.StringField(2, required=True)
	won = messages.BooleanField(3, required=True)
	guesses_made = messages.IntegerField(4, required=True)
	game_deck = messages.StringField(5, repeated=True)
	matches_found = messages.IntegerField(6, required=True, default=0)
	points = messages.IntegerField(7, required=True, default=0)


class ScoreForms(messages.Message):
	"""Return a list of ScoreForm[s]"""
	items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRanking(messages.Message):
	"""Return information regarding user rankings (players are
	ranked by points_per_guess; total_points is used to break a tie)"""
	user_name = messages.StringField(1, required=True)
	games_played = messages.IntegerField(2, required=True)
	total_guesses = messages.IntegerField(3, required=True)
	total_points = messages.IntegerField(4, required=True)
	points_per_guess = messages.IntegerField(5, required=True)


class UserRankings(messages.Message):
	"""Return a list of UserRanking[s]"""
	items = messages.MessageField(UserRanking, 1, repeated=True)


class GameHistory(messages.Message):
	"""Return GameHistory information"""
	user_name = messages.StringField(1, required=True)
	guess_history = messages.StringField(2, repeated=True)
	guesses_made = messages.IntegerField(3, required=True)
	match_list = messages.StringField(4, repeated=True)
	matches_found = messages.IntegerField(5, required=True)
	deck = messages.StringField(6, repeated=True)
	message = messages.StringField(7)


class StringMessage(messages.Message):
	"""A single outbound string message"""
	message = messages.StringField(1, required=True)
# ----------------------End message definitions----------------------
