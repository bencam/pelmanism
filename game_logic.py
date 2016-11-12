#!/usr/bin/env python


"""
The game_logic.py file contains five functions needed to play Pelmanism:

1. deck_creation() creates a list of 20 cards selected at random
2. guess_error() checks to make sure a chosen card is (a) in the deck
	and (b) is not already part of a matched pair
3. reset_deck() reset the deck so that cards flipped over in the most
	recent move are turned back over when the next move starts;
	cards that have been matched are left as an 'X'
4. won_or_lost() determines if the game is over and if the player won
	or lost; returns a variable (won_lost_msg) that is used in
	pelmanism_api.py to notify the user that the game is over
5. points() determines (if the game is over) how many points and
	points_per_guess the player earned

"""


import random
import endpoints


def deck_creation():
	"""Create a list of 20 cards selected at random"""
	# Create a starting deck of 20 cards
	cards = [
		'A',
		'A',
		'B',
		'B',
		'C',
		'C',
		'D',
		'D',
		'E',
		'E',
		'F',
		'F',
		'G',
		'G',
		'H',
		'H',
		'I',
		'I',
		'J',
		'J']

	# Set a variable for a card list to modify
	selection_deck = cards
	# Set a variable for the deck used in the game
	game_deck = []
	game_deck_counter = 0

	# Build the game deck
	while (game_deck_counter < 20):
		ran_card = random.choice(cards)
		selection_deck.remove(ran_card)
		game_deck.extend(ran_card)
		game_deck_counter += 1
	return game_deck


def guess_error(guess_int, mli):
	"""Check to make sure the chosen card is in the deck and is not
	already part of a matched pair"""
	deck_check = range(20)
	if guess_int not in deck_check:
		raise endpoints.BadRequestException(
			'Sorry, that\'s not a card in this deck. Try again.')
	if guess_int in mli:
		raise endpoints.BadRequestException(
			'Sorry, there isn\'t a card there. Try again.')


def reset_deck(disp_deck, mli):
	"""Reset the deck so that cards flipped over in the most
	recent move are turned back over when the next move starts;
	cards that have been matched are left as an 'X'"""
	for x in range(len(disp_deck)):
		if x in mli:
			disp_deck[x] = 'X'
		else:
			disp_deck[x] = '_'


def won_or_lost(game, user, guess1, guess2):
	"""Determine if the game is over and if the player won or lost;
	return the won_lost_msg"""
	# Add guess1 and guess2 to the guess_history
	history_msg = 'Guess: ' + guess1 + ', ' + guess2
	game.guess_history.append(history_msg)

	if game.matches_found == 1:
		game.end_game(True)
		user.games_played += 1
		won_lost_msg = ' You win!'
		history_end_msg = 'User %s won the game! Game over.' % user.name
		game.guess_history.append(history_end_msg)
	elif game.attempts_remaining < 1:
		game.end_game(False)
		user.games_played += 1
		won_lost_msg = ' Game over. You\'ve run out of guesses.'
		history_end_msg = 'User %s lost the game. Game over.' % user.name
		game.guess_history.append(history_end_msg)
	else:
		won_lost_msg = ''

	return won_lost_msg


def points(game, attempts_made, matches_found, user):
	"""(If the game is over) determine how many points and
	points_per_guess the player earned"""
	if game.matches_found == 1 or game.attempts_remaining < 1:
		points=(500 - ((attempts_made - matches_found) * 10))
		total_attempts = user.total_attempts
		total_points = user.total_points + points
		user.total_points = total_points
		user.points_per_guess = total_points / total_attempts
		print ''
		print 'This is the total_attempts: %s' % total_attempts
		print 'This is the total_points: %s' % total_points
		print ''


# SOURCES

# SO user Peteris Caune helped me learn how to take a random
# object from a list in python; see http://stackoverflow.com/questions/
# 18265935/python-create-list-with-numbers-between-2-values

# An SO post helped me create the deck_check list; see: http://
# stackoverflow.com/questions/18265935/python-create-list-with-
# numbers-between-2-values

# A SO discussion helped me figure out how to display chosen cards;
# see http://stackoverflow.com/questions/2582138/finding-and-
# replacing-elements-in-a-list-python
